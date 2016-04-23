import asyncio
from .tsdb_serialization import serialize, LENGTH_FIELD_LENGTH, Deserializer
from .tsdb_ops import *
from .tsdb_error import *
import json



class TSDBClient(object):
    "client"
    def __init__(self, port=9999):
        self.port = port

    def insert_ts(self, primary_key, ts):
        op = TSDBOp_InsertTS(primary_key, ts)
        serialized_json = serialize(op.to_json())
        self._send(serialized_json)

    def upsert_meta(self, primary_key, metadata_dict):
        op = TSDBOp_UpsertMeta(primary_key, metadata_dict)
        serialized_json = serialize(op.to_json())
        self._send(serialized_json)

    def select(self, metadata_dict={}, fields=None, additional=None):
        op = TSDBOp_Select(metadata_dict, fields)
        serialized_json = serialize(op.to_json())
        return self._send(serialized_json)[1]

    def augmented_select(self, proc, target, arg=None, metadata_dict={}, additional=None):
        pass

    def add_trigger(self, proc, onwhat, target, arg=None):
        op = TSDBOp_AddTrigger(proc, onwhat, target, arg)
        serialized_json = serialize(op.to_json())
        self._send(serialized_json)

    def remove_trigger(self, proc, onwhat):
        op = TSDBOp_RemoveTrigger(proc, onwhat)
        serialized_json = serialize(op.to_json())
        self._send(serialized_json)

    # Feel free to change this to be completely synchronous
    # from here onwards. Return the status and the payload

    async def _send_coro(self, msg, loop):
        reader, writer = await asyncio.open_connection('127.0.0.1', self.port, loop=loop)
        msg = (len(msg)+LENGTH_FIELD_LENGTH).to_bytes(LENGTH_FIELD_LENGTH, byteorder = 'little') + msg
        writer.write(msg)
        data = await reader.read()
        decoded = json.loads(data.decode())
        return decoded['status'], decoded['payload']

    # call `_send` with a well formed message to send.
    # once again replace this function if appropriate
    def _send(self, msg):
        loop = asyncio.get_event_loop()
        coro = asyncio.ensure_future(self._send_coro(msg, loop))
        loop.run_until_complete(coro)
        return coro.result()
