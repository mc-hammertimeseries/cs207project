import itertools
import reprlib
import numpy as np
from lazy import *


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
    # Building a TimeSeries
    >>> times = list(range(10))
    >>> values = list(range(10, 20))
    >>> timeSeries = TimeSeries(times, values)
    >>> print(timeSeries)
    TimeSeries with 10 elements: ([0, 1, 2, 3, 4, 5, ...], [10, 11, 12, 13, 14, 15, ...])

    # Accessor methods
    >>> timeSeries = TimeSeries(range(5), range(5,10))
    >>> timeSeries.times()
    array([0, 1, 2, 3, 4])
    >>> timeSeries.values()
    array([5, 6, 7, 8, 9])
    >>> timeSeries.items()
    [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]

    # Setting items
    >>> timeSeries[3]
    8
    >>> timeSeries[3] = 100
    >>> timeSeries[3]
    100

    # Interpolation
    >>> a = TimeSeries([0,5, 10], [1, 2, 3])
    >>> b = TimeSeries([2.5, 7.5], [100, -100])
    >>> a.interpolate([1])
    TimeSeries(times=([1.0], values=[1.2]))
    >>> a.interpolate(b.times())
    TimeSeries(times=([2.5, 7.5], values=[1.5, 2.5]))
    >>> a.interpolate([-100, 100])
    TimeSeries(times=([-100.0, 100.0], values=[1.0, 3.0]))

    # Lazy property
    >>> x = TimeSeries([1, 2, 3, 4],[1, 4, 9, 16])
    >>> x.lazy.eval()
    TimeSeries(times=([1, 2, 3, 4], values=[1, 4, 9, 16]))
    >>> thunk = check_length(TimeSeries(range(0,4),range(1,5)), TimeSeries(range(1,5),range(2,6)))
    >>> thunk.eval()
    True

    # Mean and median
    >>> x = TimeSeries([1, 2, 3, 4],[1, 4, 9, 16])
    >>> x.mean()
    7.5
    >>> x.median()
    6.5
    >>> x = TimeSeries([],[])
    >>> x.mean()
    Traceback (most recent call last):
        ...
    ValueError: can't take mean of empty list
    >>> x.median()
    Traceback (most recent call last):
        ...
    ValueError: can't take median of empty list
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
        idx = np.searchsorted(self._times, time)  # binary search
        # The only case when self._times[idx]!=time is when time is not in self._times
        if self._times[idx] != time:
            raise ValueError('time {} not in TimeSeries'.format(time))
        return self._values[idx]
    
    def __setitem__(self, time, value):
        """
        Sets the value corresponding to a time. Uses binary search.
        """
        idx = np.searchsorted(self._times, time)  # binary search
        # The only case when self._times[idx]!=time is when time is not in self._times
        if self._times[idx] != time:
            raise ValueError('time {} not in TimeSeries'.format(time))
        self._values[idx] = value

    def __iter__(self):
        for v in self._values:
            yield v

    def interpolate(self, time_points):
        """
        Adds an interpolating value for each point in time_points using linear
        interpolation. If a time point is already in the time series, returns the
        corresponding (time, value) pair as a TimeSeries.
        """
        new_times = np.empty_like(time_points, dtype=float)
        new_values = np.empty_like(time_points, dtype=float)

        for i, time in enumerate(time_points):
            # Check boundary conditions
            if time <= self._times[0]:
                new_times[i] = time
                new_values[i] = self._values[0]
                
            elif time >= self._times[-1]:
                new_times[i] = time
                new_values[i] = self._values[-1]
                
            else:
                # Calculate interpolation value
                idx = np.searchsorted(self._times, time)
                v_0, v_1 = self._values[idx - 1], self._values[idx]
                t_0, t_1 = self._times[idx - 1], self._times[idx]
                slope = (v_1 - v_0) / (t_1 - t_0)
                dt = time - t_0  # evaluates to 0 if time is already in time series
                new_times[i] = time
                new_values[i] = slope * dt + v_0  # evaluates to v_0 if time is already in time series

        return TimeSeries(new_times, new_values)

    def mean(self):
        if (len(self._values) == 0):
            raise ValueError("can't take mean of empty list")
        return self._values.mean()

    def median(self):
        if (len(self._values) == 0):
            raise ValueError("can't take median of empty list")
        return np.median(self._values)

    def values(self):
        return self._values

    def times(self):
        return self._times

    def items(self):
        return list(zip(self._times, self._values))

    @property
    @lazy
    def lazy(self):
        return self
        
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
        Only prints the first six times and values of the time series, in a human readable way.
        """
        class_name = type(self).__name__
        t_components = reprlib.repr(list(itertools.islice(self._times, 0, len(self))))
        t_components = t_components[t_components.find('['):]
        v_components = reprlib.repr(list(itertools.islice(self._values, 0, len(self))))
        v_components = v_components[v_components.find('['):]
        return "{} with {} elements: ({}, {})".format(class_name, len(self._times),
            t_components, v_components)

if __name__ == '__main__':
    import doctest  # Only import on running main, else not
    doctest.run_docstring_examples(TimeSeries, globals(), verbose=True, name="TimeSeries")
