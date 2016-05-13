from ..tsdb import BPlusTree
import random

def test_bplustree():
    # insert sorted additions ##########
    bt1 = BPlusTree(20)
    l = range(2000)

    for item in l:
        bt1.insert(item, str(item))

    for item in l:
        assert str(item) == bt1[item]

    assert list(l) == list(bt1)

    # insert random additions #########
    bt2 = BPlusTree(20)
    l = list(range(2000))
    random.shuffle(l)

    for item in l:
        bt2.insert(item, str(item))

    for item in l:
        assert str(item) == bt2[item]
    assert list(range(2000)) == list(bt2)

    # testing range ops ############
    range_vals = bt2.get_range("<=", 100)
    assert range_vals == ['{}'.format(i) for i in range(101)]

    range_vals = bt2.get_range("<", 100)
    assert range_vals == ['{}'.format(i) for i in range(100)]

    range_vals = bt2.get_range(">", 100)
    assert range_vals == ['{}'.format(i) for i in range(101, 2000)]

    range_vals = bt2.get_range(">=", 100)
    assert range_vals == ['{}'.format(i) for i in range(100, 2000)]

    val = bt2.get_range("==", 100)
    assert val == '100'

