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
import persistent

from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from BTrees.IFBTree import IFTreeSet, IFSet, multiunion
from BTrees.Length import Length

import zope.interface

from zope.index import interfaces

class FieldIndex(persistent.Persistent):

    zope.interface.implements(
        interfaces.IInjection,
        interfaces.IStatistics,
        interfaces.IIndexSearch,
        )

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

    def index_doc(self, docid, value):
        """See interface IInjection"""
        rev_index = self._rev_index
        if docid in rev_index:
            # unindex doc if present
            self.unindex_doc(docid)

        # Insert into forward index.
        set = self._fwd_index.get(value)
        if set is None:
            set = IFTreeSet()
            self._fwd_index[value] = set
        set.insert(docid)

        # increment doc count
        self._num_docs.change(1)

        # Insert into reverse index.
        rev_index[docid] = value

    def unindex_doc(self, docid):
        """See interface IInjection"""
        rev_index = self._rev_index
        value = rev_index.get(docid)
        if value is None:
            return # not in index

        del rev_index[docid]

        try:
            set = self._fwd_index[value]
            set.remove(docid)
        except KeyError:
            # This is fishy, but we don't want to raise an error.
            # We should probably log something.
            pass

        if not set:
            del self._fwd_index[value]

        self._num_docs.change(-1)

    def apply(self, query):
        return multiunion(self._fwd_index.values(*query))        
