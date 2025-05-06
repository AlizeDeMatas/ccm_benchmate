
import pandas as pd
from math import floor


class Range:
    def __init__(self, start, end):
        self._check_values(start, end)
        self.start = start
        self.end = end
        self._range = pd.Interval(self.start, self.end, closed='both')

    def shift(self, amount=0):
        new_start = self.start + amount
        new_end = self.end + amount
        self._check_values(new_start, new_end)
        self.start += amount
        self.end += amount
        return self

    def extend(self, start=0, end=0):
        new_start = self.start + start
        new_end = self.end + end
        self._check_values(new_start, new_end)
        self.start += start
        self.end += end
        self._range = pd.Interval(new_start, new_end, closed='both')
        return self

    def overlaps(self, other):
       return self._range.overlaps(other._range)


    def __str__(self):
        return str(f"{self.start} to {self.end}")

    def __add__(self, other):
        if type(other) is Range:
            self.start += other.start
            self.end += other.end
        elif type(other)==int:
            self.start += other
            self.end += other
        else:
            raise NotImplementedError("Can only add Ranges or integer to a Range")

        return self


    def __eq__(self, other):
        if self.start == other.start and self.end == other.end:
            return True
        else:
            return False

    def __len__(self):
        return abs(self.end - self.start)

    def _check_values(self, start, end):
        if start > end or start < 0 or end < 0:
            raise ValueError("start and end must be positive and start needs to be <= end")


class RangesList(list):
    def __init__(self, ranges):
        """
        takes a list of Range objects
        :param ranges: list of ranges
        """
        self.ranges = super().__init__(ranges)

    def find_overlap_pairs(self, other, max_gap=0):
        overlaps = []
        for i in range(len(self)):
            for j in range(len(other)):
                if self[i].overlaps(other[j].extend(start=max_gap, end=max_gap)):
                    overlaps.append((i, j))
                else:
                    continue
        return overlaps

    def find_overlaps(self, other, max_gap=0):
        pairs=self.find_overlap_pairs(other, max_gap=max_gap)
        overlaps=[(self.ranges[pair[0]], other.ranges[pair[1]]) for pair in pairs]
        return overlaps

    def __reduce__(self):
        """
        reduces the list into a single range, it will take the left and rightmost coordinates
        :return:
        """
        starts=[range.start for range in self.ranges]
        ends=[range.end for range in self.ranges]
        return Range(min(starts), max(ends))


class RangesDict(dict):
    def __init__(self, keys, values):
        """
        converst a list of ranges into a dict give a set of keys and values
        :param keys: names of the ranges
        :param values: list of Range objects
        """
        self.ranges=super().__init__()

        if len(keys) != len(values):
            raise ValueError("keys and values must have same length")
        if keys is not None and values is not None:
            for key, value in zip(keys, values):
                self.ranges[key] = value

    def find_overlaps(self, other, max_gap=0):
        pairs = self.find_overlap_pairs(other, max_gap=max_gap)
        overlaps = [(self.ranges[pair[0]], other.ranges[pair[1]]) for pair in pairs]
        return overlaps

    def find_overlap_pairs(self, other, max_gap=0):
        overlaps = []
        for key1, value1 in self.items:
            for key2, value2 in other.items:
                if self[key1].overlaps(other[key2].extend(start=max_gap, end=max_gap)):
                    overlaps.append((key1, key2))
                else:
                    continue
        return overlaps
