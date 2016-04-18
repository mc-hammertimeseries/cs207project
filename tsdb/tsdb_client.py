import asyncio
from .tsdb_serialization import serialize, LENGTH_FIELD_LENGTH, Deserializer
from .tsdb_ops import *
from .tsdb_error import *


class TSDBClient(object):
    """
    The client. This could be used in a python program, web server, or REPL!
    """

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

    def select(self, metadata_dict={}):
        op = TSDBOp_InsertTS(metadata_dict)
        serialized_json = serialize(op.to_json())
        self._send(serialized_json)

    # Feel free to change this to be completely synchronous
    # from here onwards. Return the status and the payload
    @asyncio.coroutine
    def _send_coro(self, msg, loop):
        reader, writer = yield from asyncio.open_connection('127.0.0.1', self.port, loop=loop)
        writer.write(msg)
        data = yield from reader.read()
        print('Data =', data.decode())
        return TSDBStatus.OK, payload

    # call `_send` with a well formed message to send.
    # once again replace this function if appropriate
    def _send(self, msg):
        loop = asyncio.get_event_loop()
        coro = asyncio.ensure_future(self._send_coro(msg, loop))
        loop.run_until_complete(coro)
        return coro.result()
