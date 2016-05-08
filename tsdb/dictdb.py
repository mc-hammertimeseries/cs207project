from collections import defaultdict, OrderedDict
from operator import and_
from functools import reduce
import operator

OPMAP = {
    '<': operator.lt,
    '>': operator.gt,
    '==': operator.eq,
    '!=': operator.ne,
    '<=': operator.le,
    '>=': operator.ge
}


def metafiltered(d, schema, fieldswanted):
    d2 = {}
    if len(fieldswanted) == 0:
        keys = [k for k in d.keys() if k != 'ts']
    else:
        keys = [k for k in d.keys() if k in fieldswanted]
    for k in keys:
        if k in schema:
            d2[k] = schema[k]['convert'](d[k])
    return d2


class DictDB:
    "Database implementation in a dict"

    def __init__(self, schema, pkfield):
        self.indexes = {}
        self.rows = {}
        self.schema = schema
        self.pkfield = pkfield
        for s in schema:
            indexinfo = schema[s]['index']
            if indexinfo is not None:
                self.indexes[s] = defaultdict(set)

    def insert_ts(self, pk, ts):
        "given a pk and a timeseries, insert them"
        if type(pk) != str:
            raise TypeError('Primary key must be string')
        if pk not in self.rows:
            self.rows[pk] = {'pk': pk}
        else:
            raise ValueError('Duplicate primary key found during insert')
        self.rows[pk]['ts'] = ts
        self.update_indices(pk)

    def delete_ts(self, pk):
        if type(pk) != str:
            raise TypeError('Primary key must be string')
        if pk in self.rows:
            del self.rows[pk]
        else:
            raise ValueError('Primary key is not in database')

    def upsert_meta(self, pk, meta):
        if type(pk) != str:
            raise TypeError('Primary key must be string')
        if pk not in self.rows:
            self.rows[pk] = {'pk': pk}
        for m in meta:
            if type(m) != str:
                raise TypeError('Meta key must be string')
            self.rows[pk][m] = meta[m]
        # should below be a coroutine so we dont block?
        self.update_indices(pk)

    def index_bulk(self, pks=[]):
        if len(pks) == 0:
            pks = self.rows
        for pkid in self.pks:
            self.update_indices(pkid)

    def update_indices(self, pk):
        if pk in self.rows:
            row = self.rows[pk]
            for field in row:
                v = row[field]
                if self.schema[field]['index'] is not None:
                    idx = self.indexes[field]
                    idx[v].add(pk)
        # else:
        #     for k, v in self.indexes.items():
        #         if pk in v:
        #             del v[pk]

    def select(self, meta, fields, additional):
        # if fields is None: return only pks
        # like so [pk1,pk2],[{},{}]
        # if fields is [], this means all fields
        # except for the 'ts' field. Looks like
        #['pk1',...],[{'f1':v1, 'f2':v2},...]
        # if the names of fields are given in the list, include only those fields. `ts` ia an
        # acceptable field and can be used to just return time series.
        # see tsdb_server to see how this return
        #value is used
        # additional is a dictionary. It has two possible keys:
        #(a){'sort_by':'-order'} or {'sort_by':'+order'} where order
        # must be in the schema AND have an index. (b) limit: 'limit':10
        # which will give you the top 10 in the current sort order.
        pks = []
        matchedfielddicts = []
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
                match = len(keys) > 0
                for k in keys:
                    if not isinstance(meta[k], dict):
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
        # additional filters
        if additional is not None:
            if 'sort_by' in additional:
                sortfield = additional['sort_by'][1:]
                direction = additional['sort_by'][0]
                results = list(zip(pks, [self.rows[p] for p in pks]))
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
