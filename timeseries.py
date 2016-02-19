import itertools
import reprlib
import numpy as np
from doctest import run_docstring_examples as dtest

class TimeSeries:
    """
    A class to store time series data. Supports time series data of any type, including mixed type.
    Supports all sequence operations (__getitem__, __setitem__, __len__).
    
    Attributes
    ----------
    
    Parameters
    ----------
    data : list
        a sequence of items of any type, including mixed type

    Examples
    --------
    >>> times = list(range(10))
    >>> values = list(range(10, 20))
    >>> timeSeries = TimeSeries(times, values)
    >>> print(timeSeries)
    TimeSeries with 10 elements: ([0, 1, 2, 3, 4, 5, ...], [10, 11, 12, 13, 14, 15, ...])

    >>> timeSeries = TimeSeries(range(5), range(5,10))
    >>> timeSeries.times()
    array([0, 1, 2, 3, 4])
    >>> timeSeries.values()
    array([5, 6, 7, 8, 9])
    >>> timeSeries.items()
    [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]

    >>> timeSeries[3]
    8
    >>> timeSeries[3] = 100
    >>> timeSeries[3]
    100
    """
    
    def __init__(self, times, values):
        self._times = np.array(times)
        self._values = np.array(values)

    def __contains__(self, time):
        return (time in self._times)
        
    def __len__(self):
        assert len(self._times) == len(self._values), "mismatched times and values lengths"
        return len(self._times)
    
    def __getitem__(self, time):
        """
        Gets the value corresponding to a time. Uses binary search.
        """
        idx = np.searchsorted(self._times, time) # binary search
        # the only case when self._times[idx]!=time is when time is not in self._times.
        if self._times[idx] != time:
            raise ValueError('time {} not in TimeSeries'.format(time))
        return self._values[idx]
    
    def __setitem__(self, time, value):
        """
        Sets the value corresponding to a time. Uses binary search.
        """
        idx = np.searchsorted(self._times, time) # binary search
        # the only case when self._times[idx]!=time is when time is not in self._times.
        if self._times[idx] != time:
            raise ValueError('time {} not in TimeSeries'.format(time))
        self._values[idx] = value

    def __iter__(self):
        for v in self._values:
            yield v

    def values(self):
        return self._values

    def times(self):
        return self._times

    def items(self):
        return list(zip(self._times, self._values))
        
    def __repr__(self):
        """
        Only prints the first six times and values of the time series
        """
        class_name = type(self).__name__
        t_components = reprlib.repr(list(itertools.islice(self._times, 0, len(self))))
        t_components = t_components[t_components.find('['):]
        v_components = reprlib.repr(list(itertools.islice(self._values, 0, len(self))))
        v_components = v_components[v_components.find('['):]
        return "{}(times=({}, values={}))".format(class_name, t_components, v_components)

    def __str__(self):
        """
        Only prints the first six times and values of the time series.
        """
        class_name = type(self).__name__
        t_components = reprlib.repr(list(itertools.islice(self._times, 0, len(self))))
        t_components = t_components[t_components.find('['):]
        v_components = reprlib.repr(list(itertools.islice(self._values, 0, len(self))))
        v_components = v_components[v_components.find('['):]
        return "{} with {} elements: ({}, {})".format(class_name, len(self._times),
            t_components, v_components)

if __name__ == '__main__':
    dtest(TimeSeries, globals(), verbose=True)
