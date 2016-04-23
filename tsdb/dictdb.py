from collections import defaultdict
from operator import and_
from functools import reduce
import operator

OPMAP = {
    '<': operator.lt,
    '>': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    '<=': operator.le,
    '>=': operator.ge
}


class DictDB:
    "Database implementation in a dict"

    def __init__(self, schema, pkfield):
        "initializes database with indexed and schema"
        self.indexes = {}
        self.rows = {}
        self.schema = schema
        self.pkfield = pkfield
        for s in schema:
            indexinfo = schema[s]['index']
            if indexinfo is not None:
                self.indexes[s] = defaultdict(set)

    def insert_ts(self, pk, ts):
        if type(pk) != str:
            raise TypeError('Primary key must be string')
        "given a pk and a timeseries, insert them"
        if pk not in self.rows:
            self.rows[pk] = {'pk': pk}
        else:
            raise ValueError('Duplicate primary key found during insert')
        self.rows[pk]['ts'] = ts
        self.update_indices(pk)

    def upsert_meta(self, pk, meta):
        if type(pk) != str:
            raise TypeError('Primary key must be string')
        if pk not in self.rows:
            self.rows[pk] = {'pk': pk}
        for m in meta:
            if type(m) != str:
                raise TypeError('Meta key must be string')
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

    def select(self, meta, fields):
        # if fields is None: return only pks
        # like so [pk1,pk2],[{},{}]
        # if fields is [], this means all fields
        # except for the 'ts' field. Looks like
        #['pk1',...],[{'f1':v1, 'f2':v2},...]
        # if the names of fields are given in the list, include only those fields. `ts` ia an
        # acceptable field and can be used to just return time series.
        # see tsdb_server to see how this return
        #value is used
        pks = []
        matchedfielddicts =[]
        if not meta:
            pks = self.rows.keys()
        # implement select, AND'ing over the filters in the md metadata dict
        # remember that each item in the dictionary looks like key==value
        else:
            for row in self.rows.values():
                meta_keys = set(meta.keys())
                row_keys = set(row.keys())
                # get the intersection between the keys in meta and keys and row
                keys = meta_keys & row_keys
                # For-loop
                match = len(keys) > 0
                for k in keys:
                    if type(meta[k]) is not dict:
                        if not meta[k] == row[k]:
                            match = False
                            break
                    else:
                        for op in meta[k]:
                            if not OPMAP[op](row[k], meta[k][op]):
                                match = False
                                break
                    # All filters match: return row
                if match:
                    pks.append(row['pk'])
        # If nothing is found, return None
        for pk in pks:
            field_dic = {}
            if fields is not None:
                if len(fields) == 0:
                    for k in self.rows[pk]:
                        if k != 'ts':
                            field_dic[k] = self.rows[pk][k]
                else:
                    for field in fields:
                        field_dic[field] = self.rows[pk][field]
            matchedfielddicts.append(field_dic)
        return pks, matchedfielddicts
