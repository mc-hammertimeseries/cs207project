import itertools
import reprlib
import numpy as np
from lazy import *
import operator as op
import numbers
import math
import pype


class TimeSeries:
    """
    A class to store time series data. Supports time series data of any type, including mixed type.
    Supports all sequence operations (__getitem__, __setitem__, __len__).

    Attributes
    ----------

    Parameters
    ----------
    times : list
        a sequence of floats
    values: list
        a sequence of floats

    Examples
    --------
    # Building a TimeSeries
    >>> times = list(range(10))
    >>> values = list(range(10, 20))
    >>> timeSeries = TimeSeries(times, values)
    >>> print(timeSeries)
    TimeSeries with 10 elements: ([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, ...], [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, ...])

    # Accessor methods
    >>> timeSeries = TimeSeries(range(5), range(5,10))
    >>> timeSeries.times()
    array([ 0.,  1.,  2.,  3.,  4.])
    >>> timeSeries.values()
    array([ 5.,  6.,  7.,  8.,  9.])
    >>> timeSeries.items()
    [(0.0, 5.0), (1.0, 6.0), (2.0, 7.0), (3.0, 8.0), (4.0, 9.0)]

    # Setting items
    >>> timeSeries[3]
    8.0
    >>> timeSeries[3] = 100
    >>> timeSeries[3]
    100.0

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
    TimeSeries(times=([1.0, 2.0, 3.0, 4.0], values=[1.0, 4.0, 9.0, 16.0]))
    >>> thunk = check_length(TimeSeries(range(0,4),range(1,5)), TimeSeries(range(1,5),range(2,6)))
    >>> thunk.eval()
    True

    # Mean, std and median
    >>> x = TimeSeries([1, 2, 3, 4],[1, 4, 9, 16])
    >>> x.mean()
    7.5
    >>> x.std()
    5.6789083458002736
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

    # Iterator
    >>> x = TimeSeries([1, 2, 3, 4],[1, 4, 9, 16])
    >>> for i in x.itervalues(): print(i)
    1.0
    4.0
    9.0
    16.0
    >>> for i in x.itertimes(): print(i)
    1.0
    2.0
    3.0
    4.0
    >>> for i in x.iteritems(): print(i)
    (1.0, 1.0)
    (2.0, 4.0)
    (3.0, 9.0)
    (4.0, 16.0)

    # Operators
    >>> t = TimeSeries([1,2,3], [4,5,6])
    >>> t2 = TimeSeries([1,2,3], [7,8,9])
    >>> t+t2
    TimeSeries(times=([1.0, 2.0, 3.0], values=[11.0, 13.0, 15.0]))
    >>> t-t2
    TimeSeries(times=([1.0, 2.0, 3.0], values=[-3.0, -3.0, -3.0]))
    >>> t*t2
    TimeSeries(times=([1.0, 2.0, 3.0], values=[28.0, 40.0, 54.0]))
    >>> -t
    TimeSeries(times=([1.0, 2.0, 3.0], values=[-4.0, -5.0, -6.0]))
    """

    def __init__(self, times, values):
        self._times = np.array(times, dtype=float)
        self._values = np.array(values, dtype=float)

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

    def itertimes(self):
        for t in self._times:
            yield t

    def itervalues(self):
        for v in self._values:
            yield v

    def iteritems(self):
        for (t, v) in zip(self._times, self._values):
            yield (t, v)

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
                # evaluates to v_0 if time is already in time series
                new_values[i] = slope * dt + v_0

        return TimeSeries(new_times, new_values)

    @pype.lib_import.component
    def mean(self):
        if (len(self._values) == 0):
            raise ValueError("can't take mean of empty list")
        return self._values.mean()
    
    @pype.lib_import.component
    def std(self):
        if (len(self._values) == 0):
            raise ValueError("can't take std of empty list")
        return self._values.std()
    
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

    # binary operators

    def __eq__(self, other):
        if isinstance(other, TimeSeries):
            if len(self) != len(other):
                raise ValueError(str(self) + ' and ' + str(other) +
                                 ' must have the same time points')
            self_iter = self.iteritems()
            other_iter = other.iteritems()
            for self_time, self_val in self_iter:
                other_time, other_val = next(other_iter)
                if self_time != other_time:
                    raise ValueError(str(self) + ' and ' + str(other) +
                                     ' must have the same time points')
                if self_val != other_val:
                    return False
            return True
        else:
            return NotImplemented
    """
        Generic helper function to handle binary operators that return a timeseries
    """

    def _binopt(self, other, func):
        if len(self) != len(other):
            raise ValueError(str(self) + ' and ' + str(other) + ' must have the same time points')
        times = []
        values = []
        self_iter = self.iteritems()
        other_iter = other.iteritems()
        for self_time, self_val in self_iter:
            other_time, other_val = next(other_iter)
            if self_time != other_time:
                raise ValueError(str(self) + ' and ' + str(other) +
                                 ' must have the same time points')
            times += [self_time]
            values += [func(self_val, other_val)]
        return TimeSeries(times, values)

    def __add__(self, rhs):
        try:
            if isinstance(rhs, numbers.Real):
                return TimeSeries(self._times, self._values + rhs)
            elif isinstance(rhs, TimeSeries):
                return self._binopt(rhs, op.add)
            else:
                raise NotImplemented
        except TypeError:
            raise NotImplemented

    def __radd__(self, other):
        return self + other

    def __mul__(self, rhs):
        try:
            if isinstance(rhs, numbers.Real):
                return TimeSeries(self._times, self._values * rhs)
            elif isinstance(rhs, TimeSeries):
                return self._binopt(rhs, op.mul)
            else:
                raise NotImplemented
        except TypeError:
            raise NotImplemented

    def __rmul__(self, other):
        return self * other

    def __sub__(self, rhs):
        try:
            if isinstance(rhs, numbers.Real):
                return TimeSeries(self._times, self._values - rhs)
            elif isinstance(rhs, TimeSeries):
                return self._binopt(rhs, op.sub)
            else:
                raise NotImplemented
        except TypeError:
            raise NotImplemented

    def __rsub__(self, other):
        return -self + other

    # unary operators
    def __neg__(self):
        return TimeSeries(self._times, -self._values)

    def __pos__(self):
        return TimeSeries(self._times, +self._values)

    # why are these not element-wise? says in the lab to be same semantics as vector class
    def __abs__(self):
        return math.sqrt(sum(self._values))

    def __bool__(self):
        return bool(abs(self))

if __name__ == '__main__':
    import doctest  # Only import on running main, else not
    doctest.run_docstring_examples(TimeSeries, globals(), verbose=True, name="TimeSeries")
