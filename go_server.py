#!/usr/bin/env python3
from tsdb import TSDBServer, DocDB
import timeseries as ts

identity = lambda x: x


schema = {
  'pk': {'type': "str", 'index': None},  #will be indexed anyways
  'ts': {'type': "str", 'index': None},
  'order': {'type': "int", 'index': 1},
  'blarg': {'type': "int", 'index': 1},
  'useless': {'type': "str", 'index': None},
  'mean': {'type': "float", 'index': 1},
  'std': {'type': "float", 'index': 1},
  'vp': {'type': "bool", 'index': 1}
}

NUMVPS = 5


def main():
    # we augment the schema by adding columns for 5 vantage points
    for i in range(NUMVPS):
        schema["d_vp-{}".format(i)] = {'type': "float", 'index': 1}
    db = DocDB('pk', schema=schema)
    server = TSDBServer(db)
    server.run()

if __name__=='__main__':
    main()
