# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from __future__ import division
import operator
from itertools import islice

from typing import Iterable, MutableSet, Sequence, TypeVar
from canonical_range import CanonicalRange
from cowlist import COWList
from generalized_range import generalized_range
from sortedcontainers import SortedSet

T = TypeVar('T')


class SortedFractionallyIndexedCOWListSet(MutableSet[COWList[T]], Sequence[COWList[T]]):
    """
    A set of fractionally-indexed, sorted, immutable COWList over a given alphabet.

    - Supports infinite density: always possible to insert between existing elements.
    - Alphabet must be a totally ordered, unique-letters sequence.
    - COWList must contain only letters from the initial alphabet.
    - Membership, iteration, and sequence indexing all supported.
    - `s.synthesize(index)` returns a new COWList between elements at `index - 1` and `index`.

    Example:
        s = SortedFractionallyIndexedCOWListSet(alphabet='abc')
        s.add(COWList('a'))
        pos = s.synthesize(1)  # Insert between 'a' and the 'next' element.
    """
    __slots__ = ('sorted_letter_set', 'sorted_cowlist_set')

    def __init__(self, alphabet, cowlists=()):
        # type: (Iterable[T], Iterable[COWList[T]]) -> None
        """
        Initializes a new set with a given alphabet and optional initial elements.
    
        Args:
            alphabet (Iterable[T]): An iterable of permitted symbols/letters.
            cowlists (Iterable[COWList[T]]): Optional COWLists to pre-populate the set.
    
        Raises:
            ValueError: If the given alphabet is empty or a COWList contains letters not in the alphabet.
    """
        self.sorted_letter_set = SortedSet(alphabet)
        if not self.sorted_letter_set:
            raise ValueError('Empty alphabet')

        self.sorted_cowlist_set = SortedSet()
        for cowlist in cowlists:
            self.add(cowlist)

    def __contains__(self, item):
        return self.sorted_cowlist_set.__contains__(item)

    def __getitem__(self, index):
        return self.sorted_cowlist_set.__getitem__(index)

    def __iter__(self):
        return self.sorted_cowlist_set.__iter__()

    def __len__(self):
        return self.sorted_cowlist_set.__len__()

    def __reversed__(self):
        return self.sorted_cowlist_set.__reversed__()

    def add(self, cowlist):
        # type: (COWList[T]) -> None
        """
        Adds a COWList to the set if all letters are in the alphabet.
    
        Args:
            cowlist (COWList[T]): The COWList to add.
    
        Raises:
            ValueError: If the COWList contains letters not in the alphabet.
        """
        if not all(letter in self.sorted_letter_set for letter in cowlist):
            raise ValueError('Invalid COWList: %s' % cowlist)
        else:
            self.sorted_cowlist_set.add(cowlist)

    def discard(self, cowlist):
        # type: (COWList[T]) -> None
        return self.sorted_cowlist_set.discard(cowlist)

    def synthesize(self, index):
        # type: (int) -> COWList[T]
        """
        Generates and inserts a new COWList that sorts at the specified index.
        i.e., between self[index-1] and self[index], or after the end if index == len(self).
    
        Args:
            index (int): The position at which to synthesize a new COWList.
    
        Returns:
            COWList[T]: The newly synthesized COWList, now present in the set.
    
        Raises:
            IndexError: If index is out of range (not in [-len(self), len(self)]).
            ValueError: If synthesizing a COWList smaller than all others.
        """
        length = self.sorted_cowlist_set.__len__()

        # Convert index to an offset in [0, length]
        if -length <= index < 0:
            offset = index + length
        elif 0 <= index <= length:
            offset = index
        else:
            raise IndexError('Index out of range')

        if length > 0 and offset == 0:
            raise ValueError('Cannot reliably synthesize COWList smaller than all others')

        maximum_letter = self.sorted_letter_set[-1]
        minimum_letter = self.sorted_letter_set[0]

        # We are synthesizing at the back
        if offset == length:
            # Current set is empty
            if not length:
                inserted = COWList([minimum_letter])
            # Current set is not empty
            else:
                latest = self.sorted_cowlist_set[-1]

                # Attempt to find the rearmost letter in latest that's not maximum_letter
                for index, letter in zip(CanonicalRange(len(latest), -1, -1), reversed(latest)):
                    if letter != maximum_letter:
                        prefix = latest[:index]
                        letter_one_larger = self.sorted_letter_set[self.sorted_letter_set.index(letter) + 1]
                        inserted = prefix.append(letter_one_larger)
                        break
                else:
                    # Not found?
                    # Append minimum_letter to latest
                    inserted = latest.append(minimum_letter)
        # We are synthesizing between two COWLists
        else:
            left = self.sorted_cowlist_set[offset - 1]
            right = self.sorted_cowlist_set[offset]

            left_length = len(left)
            right_length = len(right)

            # Fractional indexing: generate a COWList strictly between smaller and larger.
            n = 0
            inserted = COWList()

            while True:
                left_nth_letter = left[n] if n < left_length else minimum_letter
                right_nth_letter = right[n] if n < right_length else maximum_letter

                if left_nth_letter == right_nth_letter:
                    inserted = inserted.append(left_nth_letter)
                    n += 1
                    continue
                else:
                    letters_in_between = list(
                        islice(
                            generalized_range(
                                start=left_nth_letter,
                                stop=right_nth_letter,
                                step=1,
                                comparator=operator.lt,
                                successor=lambda letter: self.sorted_letter_set[
                                    self.sorted_letter_set.index(letter) + 1]
                            ),
                            1,
                            None
                        )
                    )

                    if letters_in_between:
                        mid_index = len(letters_in_between) // 2
                        inserted = inserted.append(letters_in_between[mid_index])
                        break
                    else:
                        inserted = inserted.append(left_nth_letter)
                        n += 1
                        continue

            while inserted in self.sorted_cowlist_set:
                inserted = inserted.append(minimum_letter)

        self.sorted_cowlist_set.add(inserted)
        return inserted
