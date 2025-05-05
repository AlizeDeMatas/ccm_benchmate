from ccm_demo.utils.ranges import Range, RangesList, RangesDict


class GenomicRanges(Range):
    def __init__(self, **kwargs):
        pass

    def find_overlaps(self, other, ignore_strand=False, max_gap=0):
        pass


class GenomicRangesList(RangesList):
    def __init__(self, **kwargs):
        pass

class GenomicRangesDict(RangesDict):
    pass



