import asyncio
from .tsdb_serialization import serialize, LENGTH_FIELD_LENGTH, Deserializer
from .tsdb_ops import *
from .tsdb_error import *

class TSDBClient(object):
    "client"
    def __init__(self, port=9999):
        self.port = port

    def insert_ts(self, primary_key, ts):
        #your code here, construct from the code in tsdb_ops.py

    def upsert_meta(self, primary_key, metadata_dict):
        msg = TSDBOp_UpsertMeta(primary_key, metadata_dict).to_json()
        print("C> msg", msg)
        self._send(msg)

    def select(self, metadata_dict={}, fields=None):
        #your code here

    def add_trigger(self, proc, onwhat, target, arg):
        # your code here

    def remove_trigger(self, proc, onwhat):
        # your code here

    async def _send_coro(self, msg, loop):
        #your code here
        return status, payload

    def _send(self, msg):
        loop = asyncio.get_event_loop()
        coro = asyncio.ensure_future(self._send_coro(msg, loop))
        loop.run_until_complete(coro)
        return coro.result()
