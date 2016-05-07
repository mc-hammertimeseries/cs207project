from tsdb import TSDBClient
import timeseries as ts
from flask import Flask, jsonify, abort, request, make_response, url_for
from multiprocessing import Process, Queue

app = Flask(__name__)
client_process = TSDBClient()

def api_helper(t):
    q = Queue()
    p = Process(target=t, args=(q,))
    p.start()
    res = q.get()
    p.join()
    return res

@app.route('/api/timeseries', methods=['POST'])
def create_task():
    return api_helper(proc_create_task)
    
def proc_create_task(q):
    if not request.json:
        return jsonify({'error': 'Missing json request data.'}), 400
    if 't' not in request.json:
        return jsonify({'error': 'Missing time data required.'}), 400
    if 'v' not in request.json:
        return jsonify({'error': 'Missing value data required.'}), 400
    if 'pk' not in request.json:
        return jsonify({'error': 'Missing pk value required.'}), 400

    new_ts = ts.TimeSeries(request.json['t'], request.json['v'])
    res = client.insert_ts(request.json['pk'], new_ts)
    print(res)
    resp = jsonify({'success': True}), 201
    q.put(resp)

if __name__ == '__main__':
    app.run(debug=True)