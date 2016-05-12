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
    
    def _load_ts(self, pk):
        filepath = 'documents/ts/' + pk + '.json'
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
        if self.schema[metakey]['type'] != 'str' and self.schema[metakey]['type'] != 'bool': # numeric
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
        # first select ts from db
        local_pks, local_matchedfielddicts = self.db.select(meta, fields, additional)
        # then select ts from disk:
        disk_pks = []
        for m in meta:
            if not isinstance(meta[m], dict):
                # if just a regular select, we'll still use the get range with == op
                metakey  = meta[m] 
                op = '=='
            else:  # otherwise, get op and metakey
                metakey, op = meta[m].keys()[0], meta[m][meta[m].keys()[0]]
            if self.schema[m]['type'] != 'str' and self.schema[m]['type'] != 'bool': # numeric
                bpt = self.indices[m]
                # use get_ranges from B+tree and then flatten
                disk_pks.append(set([item for sublist in bpt.get_ranges(op, metakey) for item in sublist]))
            else: # string or bool
                disk_pks.append(set(self.indices[m][meta[m]]))

        disk_pks = [k for k in set.intersection(*disk_pks) if k not in local_pks]

        disk_matchedfielddicts = []
        disk_allfieldsdicts = []
        for pk in disk_pks:
            ts_dict = self._load_ts(pk)
            disk_allfieldsdicts.append(ts_dict)
            if len(fields) == 0: # fields is []
                disk_matchedfielddicts.append(ts_dict)
            elif fields is None: # fields is None
                disk_matchedfielddicts.append({})
            else: 
                disk_matchedfielddicts.append({f: ts_dict[f] for f in fields if f != 'ts'})

        pks = local_pks.append(disk_pks)
        matchedfielddicts = local_matchedfielddicts.append(disk_matchedfielddicts)

        if additional is not None:
            results = list(zip(pks, [self.db.rows[p] for p in local_pks].append(disk_allfieldsdicts)))
            if 'sort_by' in additional:
                sortfield = additional['sort_by'][1:]
                direction = additional['sort_by'][0]
                if direction == '+':
                    results.sort(key=lambda x: x[1][sortfield])
                else:
                    results.sort(key=lambda x: -x[1][sortfield])
            if 'limit' in additional:
                results = results[:additional['limit']]
            results_pks = list(map(lambda x: x[0], results))
            actual_results = dict(zip(pks, matchedfielddicts))
            return results_pks, [actual_results[pk] for pk in results_pks]
        return pks, matchedfielddicts

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

