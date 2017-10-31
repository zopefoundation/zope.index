##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Field index
"""
import BTrees
import persistent
import zope.interface
from BTrees.Length import Length

from zope.index import interfaces
from zope.index.field.sorting import SortingIndexMixin

_MARKER = object()

@zope.interface.implementer(
    interfaces.IInjection,
    interfaces.IStatistics,
    interfaces.IIndexSearch,
)
class FieldIndex(SortingIndexMixin, persistent.Persistent):
    """
    A field index.

    Implements :class:`zope.index.interfaces.IInjection`,
    :class:`zope.index.interfaces.IStatistics` and
    :class:`zope.index.interfaces.IIndexSearch`.
    """

    family = BTrees.family32

    def __init__(self, family=None):
        if family is not None:
            self.family = family
        self.clear()

    def clear(self):
        """Initialize forward and reverse mappings."""
        # The forward index maps indexed values to a sequence of docids
        self._fwd_index = self.family.OO.BTree()
        # The reverse index maps a docid to its index value
        self._rev_index = self.family.IO.BTree()
        self._num_docs = Length(0)

    def documentCount(self):
        """See interface IStatistics"""
        return self._num_docs()

    def wordCount(self):
        """See interface IStatistics"""
        return len(self._fwd_index)

    def index_doc(self, docid, value):
        """See interface IInjection"""
        rev_index = self._rev_index
        if docid in rev_index:
            if docid in self._fwd_index.get(value, ()):
                # no need to index the doc, its already up to date
                return
            self.unindex_doc(docid)
        # Insert into forward index.
        set = self._fwd_index.get(value)
        if set is None:
            set = self.family.IF.TreeSet()
            self._fwd_index[value] = set
        set.insert(docid)

        # increment doc count
        self._num_docs.change(1)

        # Insert into reverse index.
        rev_index[docid] = value

    def unindex_doc(self, docid):
        """See interface IInjection"""
        rev_index = self._rev_index
        value = rev_index.get(docid, _MARKER)
        if value is _MARKER:
            return # not in index

        del rev_index[docid]

        try:
            set = self._fwd_index[value]
            set.remove(docid)
        except KeyError: #pragma NO COVERAGE
            # This is fishy, but we don't want to raise an error.
            # We should probably log something.
            # but keep it from throwing a dirty exception
            set = 1

        if not set:
            del self._fwd_index[value]

        self._num_docs.change(-1)

    def apply(self, query):
        if len(query) != 2 or not isinstance(query, tuple):
            raise TypeError("two-length tuple expected", query)
        return self.family.IF.multiunion(
            self._fwd_index.values(*query))
