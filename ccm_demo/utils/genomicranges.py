
from ccm_demo.utils.ranges import Range, RangesList, RangesDict


class GenomicRange:
    def __init__(self, chrom, start, end, strand):
        self.chrom = chrom
        self.strand = strand
        self.ranges = Range(start, end)

    def shift(self, amount):
        self.ranges=self.ranges.shift(amount)
        return self

    def extend(self, start, end):
        self.ranges=self.ranges.extend(start, end)
        return self

    def overlaps(self, other, ignore_strand=False):
        if self.chrom != other.chrom:
            raise ValueError("Genomic ranges must have same chrom")

        if not ignore_strand:
            if self.strand != other.strand:
                raise ValueError("Genomic ranges must have same strand")

        return self.ranges.overlaps(other.ranges)

    def __str__(self):
        pass

    def __eq__(self, other, ignore_strand=False):
        if self.chrom != other.chrom:
            return False
        else:
            if ignore_strand and self.strand == other.strand:
                return self.ranges == other.ranges
            else:
                return self.ranges == other.ranges


class GenomicRangesList(list):
    def __init__(self, granges):
        pass

class GenomicRangesDict(dict):
    def __init__(self, keys, granges):
        pass



