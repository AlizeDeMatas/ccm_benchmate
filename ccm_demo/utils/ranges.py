from collections import defaultdict

import pandas as pd


class Range:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return str(f"{self.start} to {self.end}")

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __reduce__(self):
        pass

    def __eq__(self, other):
        pass


class RangesList(list):
    def __init__(self, **kwargs):
        pass


class RangesDict(defaultdict):
    def __init__(self, **kwargs):
        pass