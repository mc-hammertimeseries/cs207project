import numpy.fft as nfft
import numpy as np
import timeseries as ts
from scipy.stats import norm
from .fft import fft

def tsmaker(m, s, j):
    meta={}
    meta['order'] = int(np.random.choice([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]))
    meta['blarg'] = int(np.random.choice([1, 2]))
    t = np.arange(0.0, 1.0, 0.01)
    v = norm.pdf(t, m, s) + j*np.random.randn(100)
    return meta, ts.TimeSeries(t, v)

def random_ts(a):
    t = np.arange(0.0, 1.0, 0.01)
    v = a*np.random.random(100)
    return ts.TimeSeries(t, v)

def stand(x, m, s):
    return (x-m)/s

def ccor(ts1, ts2):
    """
    Given two standardized time series, compute their cross-correlation using FFT.
    """
    v1 = ts1.values()
    v2 = ts2.values()
    N = len(v1)
    out_arr = np.empty(N, dtype=complex)
    fft.fft_ccor(np.array(v1, dtype=complex),
        np.array(v2, dtype=complex),
        out_arr)

    # out_arr is in order [0, N-1, N-2, ..., 1], so reorder it.
    return np.array(out_arr[[0] + list(range(len(out_arr)-1, 0, -1))], dtype=float)


def max_corr_at_phase(ts1, ts2):
    ccorts = ccor(ts1, ts2)
    idx = np.argmax(ccorts)
    maxcorr = ccorts[idx]
    return idx, maxcorr


#The equation for the kernelized cross correlation is given at
#http://www.cs.tufts.edu/~roni/PUB/ecml09-tskernels.pdf
#normalize the kernel there by np.sqrt(K(x,x)K(y,y)) so that the correlation
#of a time series with itself is 1.
def kernel_corr(ts1, ts2, mult=1):
    "compute a kernelized correlation so that we can get a real distance"

    def kernel(ts1,ts2):
        v1 = ts1.values()
        v2 = ts2.values()
        
        s = 0
        for i in range(len(v1)):
            shift_v2 = np.concatenate((v2[i:], v2[0:i]))
            s += np.exp(mult*np.dot(v1, shift_v2))
        return s

    return kernel(ts1, ts2) / np.sqrt(kernel(ts1, ts1) * kernel(ts2, ts2))



#this is for a quick and dirty test of these functions
#you might need to add procs to pythonpath for this to work
if __name__ == "__main__":
    print("HI")
    _, t1 = tsmaker(0.5, 0.1, 0.01)
    _, t2 = tsmaker(0.5, 0.1, 0.01)
    print(t1.mean(), t1.std(), t2.mean(), t2.std())
    import matplotlib.pyplot as plt
    plt.plot(t1)
    plt.plot(t2)
    plt.show()
    standts1 = stand(t1, t1.mean(), t1.std())
    standts2 = stand(t2, t2.mean(), t2.std())

    idx, mcorr = max_corr_at_phase(standts1, standts2)
    print(idx, mcorr)
    sumcorr = kernel_corr(standts1, standts2, mult=10)
    print(sumcorr)
    t3 = random_ts(2)
    t4 = random_ts(3)
    plt.plot(t3)
    plt.plot(t4)
    plt.show()
    standts3 = stand(t3, t3.mean(), t3.std())
    standts4 = stand(t4, t4.mean(), t4.std())
    idx, mcorr = max_corr_at_phase(standts3, standts4)
    print(idx, mcorr)
    sumcorr = kernel_corr(standts3, standts4, mult=10)
    print(sumcorr)
