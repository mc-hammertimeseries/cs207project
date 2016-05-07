from tornado import httpserver
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
import tornado.web
import tornado.escape
from tsdb import TSDBClient
from tsdb.tsdb_error import TSDBStatus
import timeseries as ts
from urllib.parse import urlparse, parse_qs

def json_error(handler, code, reason):
    handler.set_status(code)
    handler.finish({"reason":reason})    

class TimeSeriesHandler(tornado.web.RequestHandler):
    def post(self):
        if not self.request.body:
            json_error(self, 400, reason="Missing data required.")
            return
        request = tornado.escape.json_decode(self.request.body)
        if 't' not in request:
            json_error(self, 400, reason="Missing times data required.")
            return
        if 'v' not in request:
            json_error(self, 400, reason="Missing values data required.")
            return
        if 'pk' not in request:
            json_error(self, 400, reason="Missing pk data required.")
            return
        if type(request['pk']) != str:
            json_error(self, 400, reason="pk must be a string.")
            return
        try:
            new_ts = ts.TimeSeries(request['t'], request['v'])
            res = client.insert_ts(request['pk'], new_ts)
            self.write({"Status": TSDBStatus(res[0]).name})
        except BaseException as e:
            json_error(self, 400, reason=str(e))
            
    def get(self):
        o = urlparse(self.request.uri)
        query = parse_qs(o.query)
        additional = {}

        if 'limit' in query and len(query['limit']) == 1:
            additional['limit'] = query.pop('limit')[0]
        if 'sort_by' in query and len(query['sort_by']) == 1:
            additional['sort_by'] = query.pop('sort_by')[0]
            order = "+"
            if 'sort_by_increasing' in query and len(query['sort_by_increasing']) == 1:
                increasing_order = query.pop('sort_by_increasing')[0].lower()
                if increasing_order == "false" or increasing_order == "0":
                    order = "-"
            additional['sort_by'] = order + additional['sort_by']
        if len(additional) == 0:
            additional = None
        
        fields = []
        if 'fields' in query:
            fields = query.pop('fields')
            
        print(fields)
        print(additional)
        
        try:
            #new_ts = ts.TimeSeries(request['t'], request['v'])
            #res = client.insert_ts(request['pk'], new_ts)
            self.write({"Status": True})
        except BaseException as e:
            json_error(self, 400, reason=str(e))

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/api/timeseries", TimeSeriesHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


app = Application()
client = TSDBClient()

if __name__ == '__main__':
    app.listen(5000)
    IOLoop.current().start()