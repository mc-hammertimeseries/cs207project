import asyncio
from .tsdb_serialization import serialize, LENGTH_FIELD_LENGTH, Deserializer
from .tsdb_ops import *
from .tsdb_error import *
import json


class TSDBClient(object):

    def __init__(self, port=9999):
        self.port = port

    def insert_ts(self, primary_key, ts):
        op = TSDBOp_InsertTS(primary_key, ts)
        serialized_json = serialize(op.to_json())
        return self._send(serialized_json)

    def delete_ts(self, primary_key):
        op = TSDBOp_DeleteTS(primary_key)
        serialized_json = serialize(op.to_json())
        return self._send(serialized_json)

    def upsert_meta(self, primary_key, metadata_dict):
        op = TSDBOp_UpsertMeta(primary_key, metadata_dict)
        serialized_json = serialize(op.to_json())
        return self._send(serialized_json)

    def select(self, metadata_dict={}, fields=None, additional=None):
        op = TSDBOp_Select(metadata_dict, fields, additional)
        serialized_json = serialize(op.to_json())
        return self._send(serialized_json)

    def augmented_select(self, proc, target, arg=None, metadata_dict={}, additional=None):
        op = TSDBOp_AugmentedSelect(proc, target, arg, metadata_dict, additional)
        serialized_json = serialize(op.to_json())
        return self._send(serialized_json)

    def add_trigger(self, proc, onwhat, target, arg=None):
        op = TSDBOp_AddTrigger(proc, onwhat, target, arg)
        serialized_json = serialize(op.to_json())
        return self._send(serialized_json)

    def remove_trigger(self, proc, onwhat):
        op = TSDBOp_RemoveTrigger(proc, onwhat)
        serialized_json = serialize(op.to_json())
        return self._send(serialized_json)

    # Returns status and payload
    async def _send_coro(self, msg, loop):
        reader, writer = await asyncio.open_connection('127.0.0.1', self.port, loop=loop)
        writer.write(msg)
        data = await reader.read()
        d = Deserializer()
        d.append(data)
        decoded = d.deserialize()
        return decoded['status'], decoded['payload']

    # call `_send` with a well formed message to send.
    # once again replace this function if appropriate
    def _send(self, msg):
        loop = asyncio.get_event_loop()
        coro = asyncio.ensure_future(self._send_coro(msg, loop))
        loop.run_until_complete(coro)
        return coro.result()
