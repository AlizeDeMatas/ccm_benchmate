---
layout: default
title: Ranges and GenomicRanges Reference
parent: API Reference
nav_order: 4
---

<a id="ranges"></a>

# ranges

<a id="ranges.Range"></a>

## Range Objects

```python
class Range()
```

A class representing a numerical range with start and end values. inclusive

<a id="ranges.Range.__init__"></a>

#### \_\_init\_\_

```python
def __init__(start, end)
```

"

Initializes a Range object.

**Arguments**:

- `start`: The start value of the range (inclusive).
- `end`: The end value of the range (inclusive).

<a id="ranges.Range.shift"></a>

#### shift

```python
def shift(amount=0)
```

move the range by amount units, can be negative

**Arguments**:

- `amount`: which way to move the range, if positive to the right if negative to the left

**Returns**:

self but moved

<a id="ranges.Range.extend"></a>

#### extend

```python
def extend(start=0, end=0)
```

extend the range in either direction

**Arguments**:

- `start`: how much to extend the start of the range (can be negative)
- `end`: how much to extend the end of the range (can be negative)

**Returns**:

self but extended

<a id="ranges.Range.overlaps"></a>

#### overlaps

```python
def overlaps(other, type="exact")
```

determine whether two ranges overlap

**Arguments**:

- `other`: other Range to compare to
- `type`: what kind of overlap to check for, options are:
"exact": ranges are exactly the same
"within": other is completely within self
"start": other starts within self
"end": other ends within self
"any": any overlap between the two ranges

**Returns**:

bool True or False depending on whether they overlap in the specified way

<a id="ranges.Range.distance"></a>

#### distance

```python
def distance(other)
```

calculate the distance between two ranges if they overlap by any amount the distance is 0

**Arguments**:

- `other`: other Range to compare to

<a id="ranges.Range.split"></a>

#### split

```python
def split(n)
```

Splits the range into n equal parts

**Arguments**:

- `n`: number of parts to split the range into

**Returns**:

a RangesList of the split ranges

<a id="ranges.RangesList"></a>

## RangesList Objects

```python
class RangesList()
```

a list of ranges, this is a single list, the items cannot be rangeslists themselves

<a id="ranges.RangesList.__init__"></a>

#### \_\_init\_\_

```python
def __init__(ranges)
```

constructor

**Arguments**:

- `ranges`: a list of Range objects

<a id="ranges.RangesList.pop"></a>

#### pop

```python
def pop(index)
```

remove and return item at index

**Arguments**:

- `index`: index to remove if larger than length-1 will raise IndexError

**Returns**:

the item

<a id="ranges.RangesList.insert"></a>

#### insert

```python
def insert(index, value)
```

insert value at index

**Arguments**:

- `index`: index to insert at
- `value`: range to insert

**Returns**:

self

<a id="ranges.RangesList.append"></a>

#### append

```python
def append(item)
```

add to the end

**Arguments**:

- `item`: what to add

**Returns**:

self

<a id="ranges.RangesList.extend"></a>

#### extend

```python
def extend(other)
```

extend by another RangesList

**Arguments**:

- `other`: RangesList to extend by

**Returns**:

self

<a id="ranges.RangesList.find_overlaps"></a>

#### find\_overlaps

```python
def find_overlaps(other=None, type="exact", return_ranges=True)
```

find overlapping pair indices between two RangesLists, if other is none that means other is self

**Arguments**:

- `other`: other rangeslist
- `type`: what kind of overlap to check for, see Range.overlaps for options
- `return_ranges`: whether to return a tuple of indices or a tuple of ranges

**Returns**:

a tuple of overlapping pairs ranges or indices

<a id="ranges.RangesList.coverage"></a>

#### coverage

```python
def coverage()
```

calculate coverage across all ranges in the RangesList, this means the number of ranges covering each position

**Returns**:

a list of coverage values, where the index corresponds to the position relative to the minimum start position
0 index corresponds to min start position, 1 index to min start + 1

<a id="ranges.RangesList.reduce"></a>

#### reduce

```python
def reduce()
```

reduce the RangesList to a single Range that covers all ranges in the list

**Returns**:

a range that covers all ranges in the list

<a id="ranges.RangesDict"></a>

## RangesDict Objects

```python
class RangesDict(dict)
```

<a id="ranges.RangesDict.__init__"></a>

#### \_\_init\_\_

```python
def __init__(keys, values)
```

constructor

**Arguments**:

- `keys`: list of strings
- `values`: list of RangesList or Range objects

<a id="ranges.RangesDict.to_df"></a>

#### to\_df

```python
def to_df()
```

convert the RangesDict to a pandas DataFrame

0 columns: name, start, end

**Returns**:

a dataframe representation of the RangesDict

<a id="genomicranges"></a>

# genomicranges

<a id="genomicranges.GenomicRange"></a>

## GenomicRange Objects

```python
class GenomicRange()
```

Class representing a genomic range with chromosome, start, end, strand, and optional annotations.

<a id="genomicranges.GenomicRange.__init__"></a>

#### \_\_init\_\_

```python
def __init__(chrom, start, end, strand, annotation=None)
```

Initialize a GenomicRange object.

**Arguments**:

- `chrom`: Chromosome name (string)
- `start`: Genomic start (int)
- `end`: Genomic end (int)
- `strand`: Strand information ('+', '-', or '*')
- `annotation`: Optional annotation (string or dict) if string will be dict like {"annot": annotation}

<a id="genomicranges.GenomicRange.shift"></a>

#### shift

```python
def shift(amount)
```

Shift the genomic range by a specified amount.

<a id="genomicranges.GenomicRange.extend"></a>

#### extend

```python
def extend(start, end)
```

Extend the genomic range by specified amounts at start and end.

<a id="genomicranges.GenomicRange.overlaps"></a>

#### overlaps

```python
def overlaps(other, ignore_strand=False, type="any")
```

Check if this genomic range overlaps with another.

<a id="genomicranges.GenomicRange.distance"></a>

#### distance

```python
def distance(other, ignore_strand=False)
```

Calculate the distance between this genomic range and another. if they overlap, distance is 0.

<a id="genomicranges.GenomicRange.add_annotation"></a>

#### add\_annotation

```python
def add_annotation(key, value)
```

Add or update an annotation.

<a id="genomicranges.GenomicRangesList"></a>

## GenomicRangesList Objects

```python
class GenomicRangesList()
```

<a id="genomicranges.GenomicRangesList.__init__"></a>

#### \_\_init\_\_

```python
def __init__(granges)
```

Initialize a GenomicRangesList object. this cannot be a nested list.

<a id="genomicranges.GenomicRangesList.pop"></a>

#### pop

```python
def pop(index)
```

Remove and return item at index.

<a id="genomicranges.GenomicRangesList.insert"></a>

#### insert

```python
def insert(index, value)
```

Insert a GenomicRange at a specific index.

<a id="genomicranges.GenomicRangesList.append"></a>

#### append

```python
def append(item)
```

Append a GenomicRange to the list.

<a id="genomicranges.GenomicRangesList.extend"></a>

#### extend

```python
def extend(other)
```

Extend the list with another GenomicRangesList.

<a id="genomicranges.GenomicRangesList.find_overlaps"></a>

#### find\_overlaps

```python
def find_overlaps(other=None,
                  type="exact",
                  ignore_strand=False,
                  return_ranges=True)
```

Find overlaps between this GenomicRangesList and another.

**Arguments**:

- `other`: other GenomicRangesList to compare with, if none, compares with self
- `type`: what kind of overlap to look for, one of "exact", "within", "start", "end", "any"
- `ignore_strand`: whether to ignore strand information when finding overlaps
- `return_ranges`: whether to return the overlapping GenomicRange objects or their indices

**Returns**:

a list of tuples of overlapping ranges or their indices

<a id="genomicranges.GenomicRangesList.coverage"></a>

#### coverage

```python
def coverage(ignore_strand=False)
```

Calculate coverage depth at each position per chromosome and strand.

**Arguments**:

- `ignore_strand`: If True, combines coverage from both strands

**Returns**:

Dictionary of chromosomes, each containing coverage arrays
(either single array or separate arrays for + and - strands)

<a id="genomicranges.GenomicRangesList.reduce"></a>

#### reduce

```python
def reduce(ignore_strand=False)
```

Reduce overlapping or adjacent genomic ranges into minimal set of non-overlapping ranges. This will be done per chromosome

**Arguments**:

- `ignore_strand`: whether to ignore strand information when reducing

<a id="genomicranges.GenomicRangesDict"></a>

## GenomicRangesDict Objects

```python
class GenomicRangesDict(dict)
```

Class representing a dictionary of genomic ranges or lists of genomic ranges.

<a id="genomicranges.GenomicRangesDict.__init__"></a>

#### \_\_init\_\_

```python
def __init__(keys, values)
```

Initialize a GenomicRangesDict object.

<a id="genomicranges.GenomicRangesDict.to_df"></a>

#### to\_df

```python
def to_df()
```

Convert the GenomicRangesDict to a pandas DataFrame.

