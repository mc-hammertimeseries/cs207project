from ..tsdb import TSDBClient, TSDBServer, DictDB
from timeseries import TimeSeries
from collections import OrderedDict
from multiprocessing import Process
import pytest
import time

identity = lambda x: x

schema = {
    'pk': {'convert': identity, 'index': None},  # will be indexed anyways
    'ts': {'convert': identity, 'index': None},
    'order': {'convert': int, 'index': 1},
    'blarg': {'convert': int, 'index': 1},
    'useless': {'convert': identity, 'index': None},
    'mean': {'convert': float, 'index': 1},
    'std': {'convert': float, 'index': 1},
    'vp': {'convert': bool, 'index': 1}
}

orders = [0, 3, 1, 2]
blargs = [1, 1, 2, 2]
times = [0, 1, 2, 3, 4]  # Same time basis
values1 = [0, 2, 4, 6, 8]  # Two example time series values
values2 = [2, 4, 6, 8, 10]
vps = [True, False, False, True]  # Vantage points for first and last timeseries
tsrs = [TimeSeries(times, values1 if i < 2 else values2) for i in range(4)]  # only two value ranges

def setup_module(module):
    # Extend schema
    for i in range(4):
        if vps[i]:
            schema["d_vp-{}".format(i)] = {'convert': float, 'index': 1}

    # Make db
    db = DictDB(schema, 'pk')

    # Spawn server in seperate process
    global server
    global server_process
    server = TSDBServer(db)
    server_process = Process(target=server.run)
    server_process.start()

    # Give it a few seconds to initialize:
    server_process.join(2)

    # Create client
    global client
    client = TSDBClient()

    # Give it some time to get into shape
    time.sleep(2)


def test_trigger():
    # Test adding
    client.add_trigger('junk', 'insert_ts', None, 'db:one:ts')
    client.add_trigger('stats', 'insert_ts', ['mean', 'std'], None)

    # Set vantage point trigger for selected timeseries:
    for i in range(4):
        if vps[i]:
            client.add_trigger('corr', 'insert_ts', ["d_vp-{}".format(i)], tsrs[i])

    # Test remove
    client.remove_trigger('junk', 'insert_ts')

    # Give it some time to get into shape
    time.sleep(2)


def test_insert_upsert():
    for i in range(4):
        pk = 'ts-{}'.format(i)
        meta = {'order': orders[i], 'blarg': blargs[i], 'vp': vps[i]}

        # Assign one of two artificial time series we created
        ts = tsrs[i]

        # Perform test
        client.insert_ts(pk, ts)
        client.upsert_meta(pk, meta)

def test_select():
    # Select all
    results = client.select()
    result_check = OrderedDict([('ts-2', OrderedDict()),
                                ('ts-3', OrderedDict()),
                                ('ts-1', OrderedDict()),
                                ('ts-0', OrderedDict())])
    assert results[0] == 0
    for k, v in results[1].items():
        assert v == result_check[k]

    # Additionals
    results = client.select(additional={'sort_by': '-order'})
    assert results[0] == 0
    for i, key in enumerate(results[1]):
        assert orders[int(key[-1])] == list(reversed(sorted(orders)))[i]

    # Order field
    results = client.select(fields=['order'])
    result_check = OrderedDict([('ts-0', OrderedDict([('order', 0)])),
                                ('ts-2', OrderedDict([('order', 1)])),
                                ('ts-1', OrderedDict([('order', 3)])),
                                ('ts-3', OrderedDict([('order', 2)]))])
    assert results[0] == 0
    for k, v in results[1].items():
        assert v == result_check[k]

    # Get all fields
    results = client.select(fields=[])
    result_check = OrderedDict([('ts-3', OrderedDict([('pk', 'ts-3'), ('d_vp-3', 0.0), ('mean', 6.0), ('std', 2.8284271247461903), ('d_vp-0', 0.0), ('blarg', 2), ('order', 2), ('vp', True)])),
                                ('ts-2', OrderedDict([('pk', 'ts-2'), ('d_vp-3', 0.0), ('mean', 6.0), ('std', 2.8284271247461903), ('d_vp-0', 0.0), ('blarg', 2), ('order', 1), ('vp', False)])),
                                ('ts-0', OrderedDict([('pk', 'ts-0'), ('d_vp-3', 0.0), ('mean', 4.0), ('std', 2.8284271247461903), ('d_vp-0', 0.0), ('blarg', 1), ('order', 0), ('vp', True)])),
                                ('ts-1', OrderedDict([('pk', 'ts-1'), ('d_vp-3', 0.0), ('mean', 4.0), ('std', 2.8284271247461903), ('d_vp-0', 0.0), ('blarg', 1), ('order', 3), ('vp', False)]))])
    assert results[0] == 0
    for k, v in results[1].items():
        for field, fieldvalue in v.items():
            assert fieldvalue == result_check[k][field]

    # All ts with order equal to 1
    result = client.select({'order': 1}, fields=['ts'])
    result_check = OrderedDict([('ts-2', OrderedDict([('ts', [[0.0, 1.0, 2.0, 3.0, 4.0],
                                                              [2.0, 4.0, 6.0, 8.0, 10.0]])]))])
    assert result[0] == 0
    assert result[1] == result_check

    # Get all fields for ts where blarg equals 1
    results = client.select({'blarg': 1}, fields=[])
    result_check = OrderedDict([('ts-1', OrderedDict([('d_vp-3', 0.0), ('pk', 'ts-1'), ('d_vp-0', 0.0), ('std', 2.8284271247461903), ('mean', 4.0), ('vp', False), ('blarg', 1), ('order', 3)])),
                                ('ts-0', OrderedDict([('d_vp-3', 0.0), ('pk', 'ts-0'), ('d_vp-0', 0.0), ('std', 2.8284271247461903), ('mean', 4.0), ('vp', True), ('blarg', 1), ('order', 0)]))])
    assert results[0] == 0
    for k, v in results[1].items():
        for field, fieldvalue in v.items():
            assert fieldvalue == result_check[k][field]

    # Get order equals 1 and blarg equals 2
    result = client.select({'order': 1, 'blarg': 2})
    assert result[0] == 0
    assert result[1] == OrderedDict([('ts-2', OrderedDict())])

    # Get order, blarg, mean where order >= 1, sorted by descending order
    results = client.select({'order': {'>=': 1}}, fields=['order', 'blarg', 'mean'], additional={'sort_by': '-order'})
    result_check = OrderedDict([('ts-1', OrderedDict([('order', 3), ('blarg', 1), ('mean', 4.0)])), ('ts-3', OrderedDict([('order', 2), ('blarg', 2), ('mean', 6.0)])),
                                ('ts-2', OrderedDict([('order', 1), ('blarg', 2), ('mean', 6.0)]))])
    assert results[0] == 0
    for k, v in results[1].items():
        for field, fieldvalue in v.items():
            assert fieldvalue == result_check[k][field]

    # Get blarg and std where both blarg >= 1 and order is 1
    results = client.select({'blarg': {'>=': 1}, 'order': 1}, fields=['blarg', 'std'])
    result_check = OrderedDict([('ts-2', OrderedDict([('std', 2.8284271247461903), ('blarg', 2)]))])
    assert results[0] == 0
    for k, v in results[1].items():
        for field, fieldvalue in v.items():
            assert fieldvalue == result_check[k][field]


def test_augmented_select():
    # Run query
    values3 = [0.0, 4.0, 16.0, 36.0, 64.0]
    ts = TimeSeries(times, values3)
    client.insert_ts('ts-query', ts)

    # Get distance to vantage point 0
    result = client.select({'pk': 'ts-query'},fields=['d_vp-0'])[1]['ts-query']
    assert result == OrderedDict([('d_vp-0', 0.5835690085252777)])

def teardown_module(module):
    server.quit()
    server_process.terminate()
