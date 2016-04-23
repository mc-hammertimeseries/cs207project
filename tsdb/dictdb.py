from collections import defaultdict
from operator import and_
from functools import reduce


class DictDB:
    "Database implementation in a dict"

    def __init__(self, schema):
        "initializes database with indexed and schema"
        self.indexes = {}
        self.rows = {}
        self.schema = schema
        self.pkfield = 'pk'
        for s in schema:
            indexinfo = schema[s]['index']
            if indexinfo is not None:
                self.indexes[s] = defaultdict(set)

    def insert_ts(self, pk, ts):
        "given a pk and a timeseries, insert them"
        if pk not in self.rows:
            self.rows[pk] = {'pk': pk}
        else:
            raise ValueError('Duplicate primary key found during insert')
        self.rows[pk]['ts'] = ts
        self.update_indices(pk)

    def upsert_meta(self, pk, meta):
        if pk not in self.rows:
            self.rows[pk] = {'pk': pk}
        for m in meta:
            self.rows[pk][m] = meta[m]
        self.update_indices(pk)

    def index_bulk(self, pks=[]):
        if len(pks) == 0:
            pks = self.rows
        for pkid in self.pks:
            self.update_indices(pkid)

    def update_indices(self, pk):
        row = self.rows[pk]
        for field in row:
            v = row[field]
            if self.schema[field]['index'] is not None:
                idx = self.indexes[field]
                idx[v].add(pk)

    def select(self, meta):
        results = {}
        if not meta:
            return self.rows
        # implement select, AND'ing over the filters in the md metadata dict
        # remember that each item in the dictionary looks like key==value
        for row in self.rows.values():
            meta_keys = set(meta.keys())
            row_keys = set(row.keys())
            # get the intersection between the keys in meta and keys and row
            keys = meta_keys & row_keys
            # For-loop
            match = len(keys) > 0
            for k in keys:
                if not meta[k] == row[k]:
                    match = False
                    break
                # All filters match: return row
            if match:
                results[row['pk']] = row
        # If nothing is found, return None
        return results
