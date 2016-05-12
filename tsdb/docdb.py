from collections import defaultdict, OrderedDict
import operator
import json
import os
import glob
import pickle
from . import DictDB
from .btree import *
from timeseries import TimeSeries


class DocDB:
    """"
    A wrapper DB around the dict DB, for the sake of persistence.
    We update the dictDB for most operations until the user commits
    the updates to disk, at which point we will update our db on disk
    and clear out the dictDB. 
    """

    def __init__(self, pkfield, schema=None):
        if not os.path.exists('documents/'):
            os.mkdir('documents/')
        if schema == None:  # Assume it's on disk
            with open('documents/schema.json', 'r+') as file:
                self.schema = json.load(file)
        else:
            with open('documents/schema.json', 'w+') as file:
                json.dump(schema, fp=file)
                self.schema = schema

        # Make local db to be committed/flushed later
        self.db = DictDB(self.schema, pkfield)
        self.pkfield = pkfield

        # Set indices
        self.indices = {}
        self._load_indices()

        # Build indices from scratch
        if self.indices == {}:
            for s in schema:
                if schema[s] != 'pk' and schema[s] != 'ts':
                    if schema[s]['type'] != 'str' and schema[s]['type'] != 'bool':
                        # btrees for numerical fields
                        self.indices[s] = BPlusTree(6)
                    else:
                        # dictionary for strings and booleans
                        self.indices[s] = defaultdict(list)

    def _load_indices(self):
        if os.path.isfile('documents/indices.pkl'):
            with open('documents/indices.pkl', 'r+b') as f:
                self.indices = pickle.load(f)

    def _load_ts(self, pk):
        filepath = 'documents/ts/' + pk + '.json'
        with open(filepath, 'r+') as f:
            time_series = json.load(f)
        time_series['ts'] = TimeSeries(*time_series['ts'])
        return time_series

    def _serialize_index(self):
        with open('documents/indices.pkl', 'w+b') as f:
            pickle.dump(self.indices, f)

    def _serialize_ts(self, ts):
        pk = ts['pk']
        ts['ts'] = ts['ts'].to_json()
        if not os.path.exists('documents/ts/'):
            os.mkdir('documents/ts/')
        with open('documents/ts/' + pk + '.json', 'w+') as f:
            json.dump(ts, f)

    def _insert_into_index(self, pk, metakey, metaval):
        if self.schema[metakey]['type'] != 'str' and self.schema[metakey]['type'] != 'bool':  # numeric
            bpt = self.indices[metakey]
            if metaval not in bpt:
                self.indices[metakey].insert(metaval, [pk])
            else:
                self.indices[metakey].get(metaval).append(pk)
        else:  # string or bool
            self.indices[metakey][metaval].append(pk)

    def insert_ts(self, pk, ts):
        if not os.path.isfile('documents/ts/' + pk + '.json'):
            self.db.insert_ts(pk, ts)
        else:
            raise ValueError('Duplicate primary key found during insert')

    def delete_ts(self, pk):
        ts = None
        if pk in self.db.rows:
            ts = self.db.rows[pk]
            self.db.delete_ts(pk)
        elif os.path.isfile('documents/ts/' + pk + '.json'):
            ts = self._load_ts(pk)
            # Keep around for possible rollback
            os.rename('documents/ts/' + pk + '.json',
                      'documents/ts/' + pk + '.trash')
        else:
            raise KeyError(
                'Time series could not be deleted. Primary key not found')
            
        # Update indices
        for metakey, index in self.indices.items():
            if metakey in ts and metakey not in ['pk', 'ts']:
                metaval = ts[metakey]
                if self.schema[metakey]['type'] != 'str' and self.schema[metakey]['type'] != 'bool':
                    index.get(metaval).remove(pk)
                else:
                    index[metaval].remove(pk)
    
                
    def upsert_meta(self, pk, meta):
        self.db.upsert_meta(pk, meta)
        for m in meta:
            self._insert_into_index(pk, m, meta[m])

    def select(self, meta=None, fields=None, additional=None):
        # first select ts from db
        local_pks, local_matchedfielddicts = self.db.select(
            meta, fields, additional)
        # then select ts from disk:
        disk_pks = []
        if not meta:
            for doc in glob.glob('documents/ts/*.json'):
                disk_pks.append(doc.split('.')[0].split('/')[-1])
        else:
            for m in meta:
                if m == 'pk':
                    if os.path.isfile('documents/ts/' + meta[m] + '.json'):
                        disk_pks.append(set([meta[m]]))
                else:
                    if not isinstance(meta[m], dict):
                        # if just a regular select, we'll still use the get range with == op
                        metaval  = meta[m] 
                        op = '=='
                    else:  # otherwise, get op and metaval
                        op, metaval = list(meta[m].keys())[0], meta[m][list(meta[m].keys())[0]]
                    if self.schema[m]['type'] != 'str' and self.schema[m]['type'] != 'bool': # numeric
                        bpt = self.indices[m]
                        # use get_ranges from B+tree and then flatten
                        if op != '==':
                            disk_pks.append(set([item for sublist in bpt.get_range(op, metaval) for item in sublist]))
                        else:
                            disk_pks.append(set(bpt.get_range(op, metaval)))
                    else: # string or bool
                        disk_pks.append(set(self.indices[m][metaval]))
        if len(disk_pks) > 0:
            disk_pks = [k for k in set.intersection(*disk_pks) if k not in local_pks]
        disk_matchedfielddicts = []
        disk_allfieldsdicts = []
        for pk in disk_pks:
            ts_dict = self._load_ts(pk)
            disk_allfieldsdicts.append(ts_dict)
            if fields is not None:
                if len(fields) == 0:
                    disk_matchedfielddicts.append({f: ts_dict[f] for f in ts_dict.keys() if f != 'ts'})
                else: 
                    disk_matchedfielddicts.append({f: ts_dict[f] for f in fields})
            else:
                disk_matchedfielddicts.append({})
                
        pks = local_pks + disk_pks
        matchedfielddicts = local_matchedfielddicts + disk_matchedfielddicts

        if additional is not None:
            results = list(zip(pks, [self.db.rows[p]
                                     for p in local_pks].append(disk_allfieldsdicts)))
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
        try:
            # Serialize indices
            self._serialize_index()

            # Serialize time series
            all_ts = self.db.rows
            for pk in all_ts:
                self._serialize_ts(all_ts[pk])

            # Empty the local db
            self.db.rows = {}

            # Commit deletes
            to_delete = glob.glob('documents/ts/*.trash')
            for filename in to_delete:
                os.remove(filename)

        # Rollback automatically if commit fails
        except Exception as e:
            print('Encountered exception while trying to commit:')
            print(e)
            print('Rolling back...')
            self.rollback()

    def rollback(self):
        # Empty local changes
        self.db.rows = {}

        # Restore old indices
        self._load_indices()

        # Undelete time series documents that were to be deleted
        to_delete = glob.glob('documents/ts/*.trash')
        for filename in to_delete:
            stub = filename[:-6]
            os.rename(filename, stub + '.json')
