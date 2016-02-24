import timeseries as ts
from pytest import raises

def test_str():
    assert print(ts.TimeSeries(range(5), range(5,10))) == "TimeSeries with 5 elements: ([0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0])"
    
def test_len_error():
    with raises(AssertionError):
        len(ts.TimeSeries(range(1), range(2)))
        
def test_val():
    assert ts.TimeSeries(range(10), range(10,20))[5] == 15.0
    
def test_index_error():
    with raises(IndexError):
        ts.TimeSeries(range(10), range(10,20))[10]
        
def test_mean():
    assert ts.TimeSeries(range(10), range(10,20)).mean() == 14.5
    
def test_empty_mean():
    with raises(ValueError):
        ts.TimeSeries([],[]).mean()
        
def test_generator_length():
    testSeries = ts.TimeSeries(range(10), range(10,20))
    total = 0
    for val in testSeries.itervalues():
        total += val
    assert testSeries.mean() == total/len(testSeries)