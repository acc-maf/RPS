import random
from main import sort


def test_empty():
    assert sort([]) == []

def test_some():
    assert sort([5, 7, 3, 8, 1]) == [1, 3, 5, 7, 8]

def test_negative():
    assert sort([-1, -5, 3, 0]) == [-5, -1, 0, 3]


