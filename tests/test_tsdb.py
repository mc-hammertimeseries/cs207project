from ..tsdb import TSDBClient, TSDBServer, DocDB
from timeseries import TimeSeries
from procs import _corr
from collections import OrderedDict
from multiprocessing import Process
import os
import signal
import numpy as np
import pytest
import time
from rest_api import Application
from tornado.ioloop import IOLoop
import requests

schema = {
  'pk': {'type': "str", 'index': None},  #will be indexed anyways
  'ts': {'type': "str", 'index': None},
  'order': {'type': "int", 'index': 1},
  'blarg': {'type': "int", 'index': 1},
  'useless': {'type': "str", 'index': None},
  'mean': {'type': "float", 'index': 1},
  'std': {'type': "float", 'index': 1},
  'vp': {'type': "bool", 'index': 1}
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
            schema["d_vp-{}".format(i)] = {'type': "float", 'index': 1}

    # Make db
    db = DocDB('pk', schema)

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
    
    # Start restapi
    global app
    global app_process
    def run_rest():
        app = Application()
        app.listen(5000)
        IOLoop.current().start()
        
    app_process = Process(target=run_rest)
    app_process.start()
    app_process.join(2)
    
def test_rest_api():
    # test pk error
    resp = requests.post("http://localhost:5000/api/timeseries", json = {'t':list(range(1,10)), 'v':list(range(101,110))}).json()
    # test incorrect inputs
    assert resp == {'reason': 'Missing pk data required.'}
    resp = requests.post("http://localhost:5000/api/timeseries", json = {'pk':1, 'v':list(range(101,110))}).json()
    assert resp == {'reason': 'Missing times data required.'}
    resp = requests.post("http://localhost:5000/api/timeseries", json = {'pk':1, 't':list(range(101,110))}).json()
    assert resp == {'reason': 'Missing values data required.'}
    resp = requests.post("http://localhost:5000/api/timeseries").json()
    assert resp == {'reason': 'Missing data required.'}
    resp = requests.post("http://localhost:5000/api/timeseries", json = {'t':list(range(1,10)), 'v':list(range(101,110)), 'pk':1}).json()
    assert resp == {'reason': 'pk must be a string.'}
    resp = requests.post("http://localhost:5000/api/timeseries/upsert", json = {'pk':1, 'blarg':123, 'order':1}).json()
    assert resp == {'reason': 'pk must be a string.'}
    resp = requests.post("http://localhost:5000/api/timeseries", json = {'t':"wrong", 'v':"wrong", 'pk':"1"}).json()
    assert resp == {'reason': "could not convert string to float: 'wrong'"}

    # insert timeseries with pk = 1
    status = requests.post("http://localhost:5000/api/timeseries", json = {'t':list(range(1,10)), 'v':list(range(101,110)), 'pk':"1"}).json()['Status']
    assert status == 'OK'

    # rollback and make sure nothing is added
    status = requests.post("http://localhost:5000/api/rollback").json()['Status']
    assert status == 'OK'

    resp = requests.get("http://localhost:5000/api/timeseries").json()['Payload']
    assert resp == []

    # insert timeseries with pk = 1
    status = requests.post("http://localhost:5000/api/timeseries", json = {'t':list(range(1,10)), 'v':list(range(101,110)), 'pk':"1"}).json()['Status']
    assert status == 'OK'
    
    # upsert timeseries
    status = requests.post("http://localhost:5000/api/timeseries/upsert", json = {'pk':"1", 'blarg':123, 'order':1}).json()['Status']
    assert status == 'OK'

    status = requests.post("http://localhost:5000/api/commit").json()['Status']
    assert status == 'OK'

    # get timeseries
    payload = requests.get("http://localhost:5000/api/timeseries?field1=pk&value1=1&fields=blarg&fields=order").json()['Payload']
    assert payload == [['1', {'blarg': 123, 'order': 1}]]
    
    payload = requests.get("http://localhost:5000/api/timeseries?field1=order&value1=1&dtype1=int").json()['Payload']
    assert payload == [['1', {'blarg': 123, 'order': 1, 'pk': '1'}]]
    # insert second timeseries
    status = requests.post("http://localhost:5000/api/timeseries", json = {'t':list(range(1,10)), 'v':list(range(1,10)), 'pk':"2"}).json()['Status']
    assert status == 'OK'
    # upsert second timeseries
    status = requests.post("http://localhost:5000/api/timeseries/upsert", json = {'pk':"2", 'blarg':123, 'order':2}).json()['Status']
    assert status == 'OK'
    # get similarity search
    similarity = requests.get("http://localhost:5000/api/timeseries/similarity?pk1=1&sort_by=order&sort_by_increasing=false").json()['Payload']
    assert similarity == [['2', {'d_vp-1': 0.0}], ['1', {'d_vp-1': 0.0}]]
    
    # augmented handler
    payload = requests.get("http://localhost:5000/api/timeseries/augmented?proc=stats&target=mean&target=std&field1=pk&value1=1").json()['Payload']
    assert payload == [['1', {'mean': 105.0, 'std': 2.581988897471611}]]
    payload = requests.get("http://localhost:5000/api/timeseries/augmented?proc=stats&target=mean&target=std&sort_by=order&sort_by_increasing=false").json()['Payload']
    assert payload == [['2', {'mean': 5.0, 'std': 2.581988897471611}],
  ['1', {'mean': 105.0, 'std': 2.581988897471611}]]
    
    # test limit
    payload = requests.get("http://localhost:5000/api/timeseries?sort_by=order&sort_by_increasing=false").json()['Payload']
    assert payload == [['2', {'blarg': 123, 'order': 2, 'pk': '2'}],
  ['1', {'blarg': 123, 'order': 1, 'pk': '1'}]]
    payload = requests.get("http://localhost:5000/api/timeseries?sort_by=order&sort_by_increasing=true&limit=1").json()['Payload']
    assert payload == [['1', {'blarg': 123, 'order': 1, 'pk': '1'}]]
    payload = requests.get("http://localhost:5000/api/timeseries/augmented?proc=stats&target=mean&target=std&sort_by=order&sort_by_increasing=false&limit=1").json()['Payload']
    assert payload == [['2', {'mean': 5.0, 'std': 2.581988897471611}]]
    
    # improper limit test
    resp = requests.get("http://localhost:5000/api/timeseries?sort_by=order&sort_by_increasing=true&limit=wrong").json()
    assert resp == {'reason': "invalid literal for int() with base 10: 'wrong'"}
    resp = requests.get("http://localhost:5000/api/timeseries/augmented?proc=stats&target=mean&target=std&sort_by=order&sort_by_increasing=false&limit=wrong").json()
    assert resp == {'reason': "invalid literal for int() with base 10: 'wrong'"}
    
    # from and to test
    payload = requests.get("http://localhost:5000/api/timeseries?sort_by=order&sort_by_increasing=false&field1=order&from1=0&to1=1").json()['Payload']
    assert payload == [['1', {'blarg': 123, 'order': 1, 'pk': '1'}]]
    payload = requests.get("http://localhost:5000/api/timeseries/augmented?proc=stats&target=mean&target=std&sort_by=order&sort_by_increasing=false&limit=1&field1=order&from1=0&to1=1").json()['Payload']
    assert payload == [['1', {'mean': 105.0, 'std': 2.581988897471611}]]
    payload = requests.get("http://localhost:5000/api/timeseries/similarity?pk1=1&sort_by=order&sort_by_increasing=false&field1=order&value1=1&dtype1=int").json()['Payload']
    assert payload == [['1', {'d_vp-1': 0.0}]]
    
    # delete two timeseries 2, readd with random values
    status = requests.delete("http://localhost:5000/api/timeseries?pk=2").json()['Status']
    assert status == 'OK'
    status = requests.post("http://localhost:5000/api/timeseries", json = {'t':list(range(1,10)), 'v':[1,5,4,3,6,7,9,2,4], 'pk':"2"}).json()['Status']
    assert status == 'OK'
    # run similarity
    payload = requests.get("http://localhost:5000/api/timeseries/similarity?pk1=1&pk2=2&sort_by=d_vp-1&limit=1").json()['Payload']
    assert payload == [['1', {'d_vp-1': 0.0, 'd_vp-2': 1.4124686692997668}]]
    
    # delete the timeseries to clean up
    status = requests.delete("http://localhost:5000/api/timeseries?pk=1").json()['Status']
    assert status == 'OK'
    status = requests.delete("http://localhost:5000/api/timeseries?pk=2").json()['Status']
    assert status == 'OK'

    status = requests.post("http://localhost:5000/api/commit").json()['Status']
    assert status == 'OK'
    
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

def test_delete():
    client.insert_ts('test', TimeSeries(times, values1))
    client.delete_ts('test')


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
    result = client.augmented_select('stats', ['mean', 'std'], metadata_dict={'pk': 'ts-query'})[1]['ts-query']
    print('*** Result:', result)
    # assert np.isclose(result['d_vp-0'], 0.5835690085252777)

def teardown_module(module):
    os.kill(server_process.pid, signal.SIGINT)
    os.kill(app_process.pid, signal.SIGINT)

def test_corr():
    """
    Test cross-correlation functions.
    """

    arr_1 = np.linspace(1, 0, 50, dtype=complex)
    arr_2 = np.arange(0, 50, dtype=complex)
    ts_1 = TimeSeries(arr_2, arr_1)
    ts_2 = TimeSeries(arr_2, arr_2)
    out_arr = _corr.ccor(ts_1, ts_2)

    # Ensure result is consistent with numpy.fft.
    test_arr = np.fft.ifft(np.fft.fft(ts_1) * np.conj(np.fft.fft(ts_2)))
    assert np.allclose(out_arr, test_arr)

    # Test max_corr_at_phase using actual precomputed value of maxcorr.
    idx, maxcorr = _corr.max_corr_at_phase(ts_1, ts_2)
    assert idx == 25
    assert np.isclose(maxcorr, 718.87755102040819)
