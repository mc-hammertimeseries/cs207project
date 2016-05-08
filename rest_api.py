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

class TSHandler(tornado.web.RequestHandler):
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
        fields = []
        metadata_dict = {}

        if 'limit' in query:
            additional['limit'] = query['limit'][0]
        if 'sort_by' in query:
            additional['sort_by'] = query['sort_by'][0]
            order = "+"
            if 'sort_by_increasing' in query:
                increasing_order = query['sort_by_increasing'][0].lower()
                if increasing_order == "false" or increasing_order == "0":
                    order = "-"
            additional['sort_by'] = order + additional['sort_by']
        if len(additional) == 0:
            additional = None
        
        if 'fields' in query:
            fields = query['fields']
        
        i = 1
        while "field" + str(i) in query:
            field_name = query["field" + str(i)][0]
            if "from" + str(i) in query or "to" + str(i) in query:
                field_params = {}
                if "from" + str(i) in query:
                    field_params[">="] = query["from" + str(i)][0]
                if "to" + str(i) in query:
                    field_params["<="] = query["to" + str(i)][0]
                metadata_dict[field_name] = field_params
            elif "value" + str(i) in query:
                metadata_dict[field_name] = query["value" + str(i)][0]
            else:
                json_error(self, 400, reason="Query for field requires corresponding value, from, or to params, e.g. field1=colname&value1=colvalue")
                return
            i += 1
            
        try:
            res = client.select(metadata_dict, fields, additional)
            self.write({"Status": TSDBStatus(res[0]).name, "Payload":res[1]})
        except BaseException as e:
            json_error(self, 400, reason=str(e))
    
class TSUpsertHandler(tornado.web.RequestHandler):
    def post(self):
        if not self.request.body:
            json_error(self, 400, reason="Missing data required.")
            return
        request = tornado.escape.json_decode(self.request.body)
        if 'pk' not in request:
            json_error(self, 400, reason="pk required for upsert.")
            return
        if type(request['pk']) != str:
            json_error(self, 400, reason="pk must be a string.")
            return
        pk = request.pop("pk")
        
        try:
            res = client.upsert_meta(pk, request)
            self.write({"Status": TSDBStatus(res[0]).name})
        except BaseException as e:
            json_error(self, 400, reason=str(e))
            
class TSAugmentHandler(tornado.web.RequestHandler):
    def get(self):
        o = urlparse(self.request.uri)
        query = parse_qs(o.query)
        
        if 'proc' not in query:
            json_error(self, 400, reason="proc must be specified in augmented select.")
            return
        if 'target' not in query:
            json_error(self, 400, reason="target must be specified in augmented select.")
            return
        proc = query['proc'][0]
        target = query['target']
        arg = None
        if 'arg' in query:
            arg = query['arg'][0]
        metadata_dict = {}
        additional = {}
        
        if 'limit' in query:
            additional['limit'] = query['limit'][0]
        if 'sort_by' in query:
            additional['sort_by'] = query['sort_by'][0]
            order = "+"
            if 'sort_by_increasing' in query:
                increasing_order = query['sort_by_increasing'][0].lower()
                if increasing_order == "false" or increasing_order == "0":
                    order = "-"
            additional['sort_by'] = order + additional['sort_by']
        if len(additional) == 0:
            additional = None
        
        i = 1
        while "field" + str(i) in query:
            field_name = query["field" + str(i)][0]
            if "from" + str(i) in query or "to" + str(i) in query:
                field_params = {}
                if "from" + str(i) in query:
                    field_params[">="] = query["from" + str(i)][0]
                if "to" + str(i) in query:
                    field_params["<="] = query["to" + str(i)][0]
                metadata_dict[field_name] = field_params
            elif "value" + str(i) in query:
                metadata_dict[field_name] = query["value" + str(i)][0]
            else:
                json_error(self, 400, reason="Query for field requires corresponding value, from, or to params, e.g. field1=colname&value1=colvalue")
                return
            i += 1
            
        try:
            res = client.augmented_select(proc, target, arg, metadata_dict, additional)
            self.write({"Status": TSDBStatus(res[0]).name, "Payload":res[1]})
        except BaseException as e:
            json_error(self, 400, reason=str(e))

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/api/timeseries", TSHandler),
            (r"/api/timeseries/upsert", TSUpsertHandler),
            (r"/api/timeseries/augmented", TSAugmentHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


app = Application()
client = TSDBClient()

if __name__ == '__main__':
    app.listen(5000)
    IOLoop.current().start()