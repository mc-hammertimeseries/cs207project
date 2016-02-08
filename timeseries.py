import itertools
import reprlib

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
    """
    
    def __init__(self, data):
        self._length = len(data)
        self._data = [None] * self._length
        for idx, value in enumerate(data):
            self._data[idx] = value
        
    def __len__(self):
        return self._length
    
    def __getitem__(self, idx):
        return self._data[idx]
    
    def __setitem__(self, idx, value):
        self._data[idx] = value
        
    def __repr__(self):
        class_name = type(self).__name__
        components = reprlib.repr(list(itertools.islice(self._data, 0, self._length)))
        components = components[components.find('['):]
        return "{}(data={})".format(class_name, components)
        
        
    def __str__(self):
        """
        Only prints the first six elements of the time series.
        """
        class_name = type(self).__name__
        components = reprlib.repr(list(itertools.islice(self._data, 0, self._length)))
        components = components[components.find('['):]
        return "{} with {} elements: {}".format(class_name, self._length, components)