##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

$Id$
"""
from persistent import Persistent

from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from BTrees.IIBTree import IITreeSet, IISet, union
from BTrees.Length import Length

from types import ListType, TupleType
from zope.interface import implements

from zope.index.interfaces import IInjection, ISimpleQuery
from zope.index.interfaces import IStatistics, IRangeQuerying


class FieldIndex(Persistent):

    implements(IRangeQuerying, IInjection, ISimpleQuery, IStatistics)

    def __init__(self):
        self.clear()

    def clear(self):
        """Initialize forward and reverse mappings."""
        # The forward index maps indexed values to a sequence of docids
        self._fwd_index = OOBTree()
        # The reverse index maps a docid to its index value
        self._rev_index = IOBTree()
        self._num_docs = Length(0)

    def documentCount(self):
        """See interface IStatistics"""
        return self._num_docs()

    def wordCount(self):
        """See interface IStatistics"""
        return len(self._fwd_index)

    def has_doc(self, docid):
        return bool(self._rev_index.has_key(docid))

    def index_doc(self, docid, value):
        """See interface IInjection"""
        if self.has_doc(docid):       # unindex doc if present
            self.unindex_doc(docid)
        self._insert_forward(docid, value)
        self._insert_reverse(docid, value)

    def unindex_doc(self, docid):
        """See interface IInjection"""
        try:      # ignore non-existing docids, don't raise
            value = self._rev_index[docid]
        except KeyError:
            return

        del self._rev_index[docid]

        try:
            self._fwd_index[value].remove(docid)
            if len(self._fwd_index[value]) == 0:
                del self._fwd_index[value]
        except KeyError:
            pass
        self._num_docs.change(-1)

    def search(self, values):
        "See interface ISimpleQuerying"
        # values can either be a single value or a sequence of
        # values to be searched.
        if isinstance(values, (ListType, TupleType)):
            result = IISet()
            for value in values:
                try:
                    r = IISet(self._fwd_index[value])
                except KeyError:
                    continue
                # the results of all subsearches are combined using OR
                result = union(result, r)
        else:
            try:
                result = IISet(self._fwd_index[values])
            except KeyError:
                result = IISet()

        return result

    def query(self, querytext, start=0, count=None):
        """See interface IQuerying"""
        res = self.search(querytext)
        if start or count:
            res = res[start:start+count]
        return res

    def rangesearch(self, minvalue, maxvalue):
        return IISet(self._fwd_index.keys(minvalue, maxvalue))

    def _insert_forward(self, docid, value):
        """Insert into forward index."""
        if not self._fwd_index.has_key(value):
            self._fwd_index[value] = IITreeSet()
        self._fwd_index[value].insert(docid)
        self._num_docs.change(1)

    def _insert_reverse(self, docid, value):
        """Insert into reverse index."""
        self._rev_index[docid] = value
