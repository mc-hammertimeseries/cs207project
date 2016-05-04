from ..tsdb import TSDBClient, TSDBServer, DictDB
from ..timeseries import TimeSeries
from collections import OrderedDict
import pytest
from multiprocessing import Process

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


def test_trigger():
    # Test adding
    client.add_trigger('junk', 'insert_ts', None, 'db:one:ts')
    client.add_trigger('stats', 'insert_ts', ['mean', 'std'], None)

    # Set vantage point trigger for selected timeseries:
    for i in range(4):
        if vps[i]:
            client.add_trigger('corr', 'insert_ts', ["d_vp-{}".format(i)],
                               'ts-{}'.format(i))

    # Test remove
    client.remove_trigger('junk', 'insert_ts')


def test_insert_upsert():
    for i in range(4):
        pk = 'ts-{}'.format(i)
        meta = {'order': orders[i], 'blarg': blargs[i], 'vp': vps[i]}
        print(meta)

        # Assign one of two artificial time series we created
        ts = TimeSeries(times, values1 if i < 2 else values2)

        # Trigger a corr when vp is enabled
        if vps[i]:
            client.add_trigger('corr', 'insert_ts', ["d_vp-{}".format(i)], pk)

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
    result_check = OrderedDict([('ts-0', OrderedDict([('pk', 'ts-0'), ('vp', True), ('blarg', 1), ('order', 0)])),
                                ('ts-1', OrderedDict([('pk', 'ts-1'), ('vp', False), ('blarg', 1), ('order', 3)])),
                                ('ts-3', OrderedDict([('pk', 'ts-3'), ('vp', True), ('blarg', 2), ('order', 2)])),
                                ('ts-2', OrderedDict([('pk', 'ts-2'), ('vp', False), ('blarg', 2), ('order', 1)]))])
    assert results[0] == 0
    for k, v in results[1].items():
        for field, fieldvalue in v.items():
            assert fieldvalue == result_check[k][field]

    # All ts with order equal to 1
    result = client.select({'order': 1}, fields=['ts'])
    result_check = OrderedDict([('ts-2', OrderedDict([('ts', [[0.0, 1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0, 10.0]])]))])
    assert result[0] == 0
    assert result[1] == result_check

    # Get all fields for ts where blarg equals 1
    results = client.select({'blarg': 1}, fields=[])
    result_check = OrderedDict([('ts-1', OrderedDict([('blarg', 1), ('order', 3), ('pk', 'ts-1'), ('vp', False)])),
                                ('ts-0', OrderedDict([('blarg', 1), ('order', 0), ('pk', 'ts-0'), ('vp', True)]))])
    assert results[0] == 0
    for k, v in results[1].items():
        for field, fieldvalue in v.items():
            assert fieldvalue == result_check[k][field]

    # Get order equals 1 and blarg equals 2
    result = client.select({'order': 1, 'blarg': 2})
    assert result[0] == 0
    assert result[1] == OrderedDict([('ts-2', OrderedDict())])

    print('------------order >= 1  order, blarg and mean sent back, also sorted---------')
    results = client.select({'order': {'>=': 1}}, fields=['order', 'blarg', 'mean'], additional={'sort_by': '-order'})
    print(results)
#
#     print('------------order 1 blarg >= 1 fields blarg and std---------')
#     _, results = client.select({'blarg': {'>=': 1}, 'order': 1}, fields=['blarg', 'std'])
#     for k in results:
#         print(k, results[k])


def test_augmented_select():
    pass


def teardown_module(module):
    server.quit()
    server_process.terminate()
