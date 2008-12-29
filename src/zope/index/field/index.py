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
import heapq
import bisect
from itertools import islice

import BTrees
import persistent
import zope.interface
from BTrees.Length import Length

from zope.index import interfaces

class FieldIndex(persistent.Persistent):

    zope.interface.implements(
        interfaces.IInjection,
        interfaces.IStatistics,
        interfaces.IIndexSearch,
        interfaces.IIndexSort,
        )

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
            # unindex doc if present
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

    def sort(self, docids, limit=None, reverse=False):
        if (limit is not None) and (limit < 1):
            raise ValueError('limit value must be 1 or greater')

        numdocs = self._num_docs.value
        if not numdocs:
            raise StopIteration

        if not isinstance(docids, (self.family.IF.Set, self.family.IF.TreeSet)):
            docids = self.family.IF.Set(docids)
        if not docids:
            raise StopIteration

        rlen = len(docids)

        fwd_index = self._fwd_index
        rev_index = self._rev_index
        getValue = rev_index.get
        marker = object()

        # use_lazy and use_nbest computations lifted wholesale from
        # Zope2 catalog without questioning reasoning
        use_lazy = rlen > numdocs * (rlen / 100 + 1)
        use_nbest = limit and limit * 4 < rlen

        # overrides for unit tests
        if getattr(self, '_use_lazy', False):
            use_lazy = True
        if getattr(self, '_use_nbest', False):
            use_nbest = True
        
        if use_nbest:
            # this is a sort with a limit that appears useful, try to
            # take advantage of the fact that we can keep a smaller
            # set of simultaneous values in memory; use generators
            # and heapq functions to do so.

            def nsort():
                for docid in docids:
                    val = getValue(docid, marker)
                    if val is not marker:
                        yield (val, docid)

            iterable = nsort()

            if reverse:
                # we use a generator as an iterable in the reverse
                # sort case because the nlargest implementation does
                # not manifest the whole thing into memory at once if
                # we do so.
                for val in heapq.nlargest(limit, iterable):
                    yield val[1]
            else:
                # lifted from heapq.nsmallest
                it = iter(iterable)
                result = sorted(islice(it, 0, limit))
                if not result:
                    raise StopIteration
                insort = bisect.insort
                pop = result.pop
                los = result[-1]    # los --> Largest of the nsmallest
                for elem in it:
                    if los <= elem:
                        continue
                    insort(result, elem)
                    pop()
                    los = result[-1]
                for val in result:
                    yield val[1]

        else:
            if use_lazy and not reverse:
                # Since this the sort is not reversed, and the number
                # of results in the search result set is much larger
                # than the number of items in this index, we assume it
                # will be fastest to iterate over all of our forward
                # BTree's items instead of using a full sort, as our
                # forward index is already sorted in ascending order
                # by value. The Zope 2 catalog implementation claims
                # that this case is rarely exercised in practice.
                n = 0
                for stored_docids in fwd_index.values():
                    for docid in self.family.IF.intersection(docids, stored_docids):
                        n += 1
                        yield docid
                        if limit and n >= limit:
                            raise StopIteration
            else:
                # If the result set is not much larger than the number
                # of documents in this index, or if we need to sort in
                # reverse order, use a non-lazy sort.
                n = 0
                for docid in sorted(docids, key=getValue, reverse=reverse):
                    if getValue(docid, marker) is not marker:
                        n += 1
                        yield docid
                        if limit and n >= limit:
                            raise StopIteration
