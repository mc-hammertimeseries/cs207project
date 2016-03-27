#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from cs207project.skeleton import fib

__author__ = "Jonathan Friedman"
__copyright__ = "Jonathan Friedman"
__license__ = "none"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
