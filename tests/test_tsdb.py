from ..tsdb import TSDBClient, TSDBServer, DictDB
from ..timeseries import TimeSeries
import time
import pytest
import numpy as np
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

orders = [0, 1, 1, 2]
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
    print('trigger', client)
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
    print('insert', client)
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
    print('Got upserts')

# def test_select():
#     print('---------DEFAULT------------')
#     print(client.select())
#
#     print('---------ADDITIONAL------------')
#     client.select(additional={'sort_by': '-order'})
#
#     print('----------ORDER FIELD-----------')
#     _, results = client.select(fields=['order'])
#     for k in results:
#         print(k, results[k])
#
#     print('---------ALL FIELDS------------')
#     client.select(fields=[])
#
#     print('------------TS with order 1---------')
#     client.select({'order': 1}, fields=['ts'])
#
#     print('------------All fields, blarg 1 ---------')
#     client.select({'blarg': 1}, fields=[])
#
#     print('------------order 1 blarg 2 no fields---------')
#     _, bla = client.select({'order': 1, 'blarg': 2})
#     print(bla)
#
#     print('------------order >= 4  order, blarg and mean sent back, also sorted---------')
#     _, results = client.select({'order': {'>=': 4}}, fields=['order', 'blarg', 'mean'], additional={'sort_by': '-order'})
#     for k in results:
#         print(k, results[k])
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
