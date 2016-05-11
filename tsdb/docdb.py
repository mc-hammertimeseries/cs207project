from collections import defaultdict, OrderedDict
from operator import and_
from functools import reduce
import operator
import json
import os
import pickle
from . import DictDB, BPlusTree
from timeseries import TimeSeries

OPMAP = {
    '<': operator.lt,
    '>': operator.gt,
    '==': operator.eq,
    '!=': operator.ne,
    '<=': operator.le,
    '>=': operator.ge
}

class DocDB:
    """"
    A wrapper DB around the dict DB, for the sake of persistence.
    We update the dictDB for most operations until the user commits
    the updates to disk, at which point we will update our db on disk
    and clear out the dictDB. 
    """

    def __init__(self, schema, pkfield):
        self.db = DictDB(schema, pkfield) # have a d
        with open('documents/schema.json', 'w+') as file:
            json.dump(schema, fp=file)

        self.schema = schema
        self.pkfield = pkfield
        self.indices = {}
        for s in schema:
            if schema[s] != 'pk' and schema[s] != 'ts':
                if schema[s]['type'] != 'str' and  schema[s]['type'] != 'bool':
                   self.indices[s] = BPlusTree(6) # btrees for numerical fields 
                else: 
                    self.indices[s] = defaultdict(list) # dictionary for strings and booleans
    
    def _deserialize_ts(self, filepath):
        with open(filepath, 'r+') as f:
            time_series = json.load(f)
        time_series['ts'] = TimesSeries(*time_series['ts'])
        return time_series

    def _serialize_index(self):
        with open('documents/indices.pkl', 'w+b') as f:
            pickle.dump(self.indices, f)

    def _serialize_ts(self, ts):
        pk = ts['pk']
        ts['ts'] = ts['ts'].to_json()
        with open('documents/ts/' + pk + '.json', 'w+b') as f:
            json.dump(ts, f)
            
    def _insert_into_index(self, pk, metakey, metaval):
        if schema[metakey]['type'] != 'str' and schema[metakey]['type'] != 'bool': # numeric
            bpt = self.indices[metakey]
            if metaval not in bpt:
                self.indices[metakey].insert(metaval,[pk])
            else: 
                self.indices[metakey].get(metaval).append(pk)
        else: # string or bool
            self.indices[metakey][metaval].append(pk)

    def insert_ts(self, pk, ts):
        if not os.path.isfile('documents/ts/' + pk + '.json'):
            self.db.insert_ts(pk, ts)
        else:
            raise ValueError('Duplicate primary key found during insert')

    def upsert_meta(self, pk, meta):
        self.db.upsert_meta(pk, meta)
        for m in meta:
            self._insert_into_index(pk, m, meta[m])

    def select(self, meta, fields, additional):

        # load relevant files 
            # if not already in dictDB, add them
        # perform query on that dictDB

    def commit(self):
        # serialize indices
        self._serialize_index()
        # serialize time series
        all_ts = self.db.rows
        for pk in all_ts:
            self._serialize_ts(all_ts[pk])

        self.db.rows = {}

if __name__ == "__main__":

    schema = {
      'pk': {'type': 'str', 'index': None},  #will be indexed anyways
      'ts': {'type': 'ts', 'index': None},
      'order': {'type': 'int', 'index': 1},
      'blarg': {'type': 'int', 'index': 1},
      'useless': {'type': 'str', 'index': None},
      'mean': {'type': 'float', 'index': 1},
      'std': {'type': 'float', 'index': 1},
      'vp': {'type': 'bool', 'index': 1}
    }

    db = DocDB(schema,'pk')

