# `sorted-fractionally-indexed-cowlist-set`

A Python package for managing a sorted, fractionally-indexed set of COWList containing elements within a given alphabet.

## Motivation

Many applications (real-time collaborative editors, distributed ledgers, dynamic sorted tables) require the ability to
insert an unlimited number of unique items "in between" others in a totally ordered collection. This library brings this
power to Python, modeled after the "fractional indexing" algorithms used in CRDTs and scalable databases.

## Features

- Infinite-density insertion: Always able to create new COWList *between* or *after* existing members (fractional
  indexing).
- Efficient membership, indexing, and iteration.
- Fully typed.
- Supports Python 2 and 3.
- No non-Python dependencies.

Perfect for collaborative editing, database indices, and any system requiring dynamic totally ordered unique keys.

## Installation

```bash
pip install sorted-fractionally-indexed-cowlist-set
```

## Usage

```python
# coding=utf-8
from __future__ import print_function
from cowlist import COWList
from sorted_fractionally_indexed_cowlist_set import SortedFractionallyIndexedCOWListSet

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

# Initialize with base58 (or your own custom alphabet)
s = SortedFractionallyIndexedCOWListSet(alphabet=BASE58_ALPHABET)

# Synthesize an initial COWList
initial = s.synthesize(index=0)

# Cannot reliably synthesize COWList smaller than all others
try:
    s.synthesize(index=0)
except ValueError:
    pass

# Add existing COWList
s.add(COWList('4fj8AiZ'))
s.add(COWList('X'))

# Edge: try to add an invalid COWList
# Notice uppercase I is NOT in BASE58!
try:
    s.add(COWList('I'))
except ValueError:
    pass

# Check membership
assert COWList('X') in s

# List all COWLists (iteration is in sorted order)
assert list(s) == [
    initial,
    COWList('4fj8AiZ'),
    COWList('X')
]

# Support for sequence protocol
assert len(s) == 3
assert s[0] == initial
assert s[1] == COWList('4fj8AiZ')

# Fractional insertion
# Insert a new COWList "between" the first and second elements
mid = s.synthesize(index=1)
assert list(s) == [
    initial,
    mid,
    COWList('4fj8AiZ'),
    COWList('X')
]

# You can insert at back
back = s.synthesize(index=len(s))
assert list(s) == [
    initial,
    mid,
    COWList('4fj8AiZ'),
    COWList('X'),
    back
]

# Reverse iteration (sorted high-to-low)
assert list(reversed(s)) == [
    back,
    COWList('X'),
    COWList('4fj8AiZ'),
    mid,
    initial
]

# Discarding COWLists
s.discard(COWList('4fj8AiZ'))
s.discard(COWList('notpresent'))

assert list(s) == [
    initial,
    mid,
    COWList('X'),
    back
]

# Slicing like a sequence
# Returns a List[COWList]
assert s[1:4] == [
    mid,
    COWList('X'),
    back
]
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).