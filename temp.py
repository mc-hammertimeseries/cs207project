import shutil
from tsdb import DocDB
from timeseries import TimeSeries

schema = {
    'pk': {'type': 'str', 'index': None},  # will be indexed anyways
    'ts': {'type': 'ts', 'index': None},
    'order': {'type': 'int', 'index': 1},
    'blarg': {'type': 'int', 'index': 1},
    'useless': {'type': 'str', 'index': None},
    'mean': {'type': 'float', 'index': 1},
    'std': {'type': 'float', 'index': 1},
    'vp': {'type': 'bool', 'index': 1}
}

#shutil.rmtree('documents/')

db = DocDB('pk')

orders = [0, 3, 1, 2]
blargs = [1, 1, 2, 2]
times = [0, 1, 2, 3, 4]  # Same time basis
values1 = [0, 2, 4, 6, 8]  # Two example time series values
values2 = [2, 4, 6, 8, 10]
vps = [True, False, False, True]  # Vantage points for first and last timeseries
tsrs = [TimeSeries(times, values1 if i < 2 else values2) for i in range(4)]  # only two value ranges

# for i in range(4):
#     db.insert_ts('ts-{}'.format(i), tsrs[i])
# 
# for i in range(4):
#     db.upsert_meta('ts-%i' % i, {'order': orders[i], 'blarg': blargs[i], 'vp': vps[i]})
# 
# db.commit()
# 
# for i in range(4, 8):
#     db.insert_ts('ts-{}'.format(i), tsrs[i-4])
# 
# for i in range(4, 8):
#     db.upsert_meta('ts-%i' % i, {'order': orders[i-4], 'blarg': blargs[i-4], 'vp': vps[i-4]})
# 
# 
# db.delete_ts('ts-0')
# 
# #db.rollback()
# 
# db.commit()

print(db.select({'order': {'<=': 2}, 'blarg': {'<': 2}}))
