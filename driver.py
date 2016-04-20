#!/usr/bin/env python3

import sys
import pype
import timeseries

ts_1 = timeseries.TimeSeries(range(100), range(-50, 50))

for fname in sys.argv[1:]:
	pipeline = pype.Pipeline(fname)
	value = pipeline['standardize'].run(ts_1)
	print(value)
	print (value.mean(), value.std())