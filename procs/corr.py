import timeseries as ts
import numpy as np
import asyncio
from ._corr import stand, kernel_corr


# this function is directly used for augmented selects
def proc_main(pk, row, arg):
    #The argument is a time series. But due to serialization it does
    #not come out as the "instance", and must be cast
    argts = ts.TimeSeries(*arg)
    #compute a standardized time series
    stand_argts = stand(argts, argts.mean(), argts.std())
    # for each row in our select/etc, standardize the time series
    stand_rowts = stand(row['ts'], row['ts'].mean(), row['ts'].std())
    #compute the normalized kernelized cross-correlation
    kerncorr = kernel_corr(stand_rowts, stand_argts, 5)
    # compute a distance from it.
    #The distance is given by np.sqrt(K(x,x) + K(y,y) - 2*K(x,y))
    #since we are normalized the autocorrs are 1
    kerndist = np.sqrt(2*(1-kerncorr))
    return [kerndist]
    # return [np.dot(stand_rowts.values()-stand_argts.values(),stand_rowts.values()-stand_argts.values())]

#the function is wrapped in a coroutine for triggers
async def main(pk, row, arg):
    return proc_main(pk, row, arg)
