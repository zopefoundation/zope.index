##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Keyword index"""

from persistence import Persistent

from zodb.btrees.IOBTree import IOBTree
from zodb.btrees.OOBTree import OOBTree, OOSet
from zodb.btrees.IIBTree import IISet, union, intersection

from types import ListType, TupleType, StringTypes
from zope.index.interfaces import IInjection, IKeywordQuerying, IStatistics
from zope.interface import implements

class KeywordIndex(Persistent):

    implements(IInjection, IStatistics, IKeywordQuerying)

    def __init__(self):
        self.clear()

    def clear(self):
        """Initialize forward and reverse mappings."""

        # The forward index maps index keywords to a sequence of docids
        self._fwd_index = OOBTree()

        # The reverse index maps a docid to its keywords
        # TODO: Using a vocabulary might be the better choice to store
        # keywords since it would allow use to use integers instead of
        # strings
        self._rev_index = IOBTree()

    def documentCount(self):
        """Return the number of documents in the index."""
        return len(self._rev_index)

    def wordCount(self):
        """Return the number of indexed words"""
        return len(self._fwd_index)

    def has_doc(self, docid):
        return bool(self._rev_index.has_key(docid))

    def index_doc(self, docid, seq):

        seq = [w.lower() for w in seq]
            
        if self.has_doc(docid):       # unindex doc if present
            self.unindex_doc(docid)

        if not isinstance(seq, (TupleType, ListType)):
            raise TypeError, 'seq argument must be a list/tuple of strings'

        self._insert_forward(docid, seq)
        self._insert_reverse(docid, seq)

    def unindex_doc(self, docid):

        idx  = self._fwd_index

        try:
            for word in self._rev_index[docid]:
                idx[word].remove(docid)
                if not idx[word]: del idx[word] 
        except KeyError: pass
        
        try:
            del self._rev_index[docid]
        except KeyError: pass


    def _insert_forward(self, docid, words):
        """insert a sequence of words into the forward index """

        idx = self._fwd_index
        has_key = idx.has_key
        for word in words:
            if not has_key(word):
                idx[word] = IISet()
            idx[word].insert(docid)

    def _insert_reverse(self, docid, words):
        """ add words to forward index """

        if words:  
            self._rev_index[docid] = OOSet(words)

    def search(self, query, operator='and'):

        if isinstance(query, StringTypes): query = [query]
        if not isinstance(query, (TupleType, ListType)):
            raise TypeError, 'query argument must be a list/tuple of strings'

        query = [w.lower() for w in query]

        f = {'and' : intersection, 'or' : union}[operator]
    
        rs = None
        for word in query:
            docids = self._fwd_index.get(word, IISet())
            rs = f(rs, docids)
            
        if rs:  return rs
        else: return IISet()
        
