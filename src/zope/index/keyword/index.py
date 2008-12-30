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
"""Keyword index

$Id$
"""
from persistent import Persistent

import BTrees

from BTrees.Length import Length

from zope.index.interfaces import IInjection, IStatistics, IIndexSearch
from zope.index.keyword.interfaces import IKeywordQuerying
from zope.interface import implements


class KeywordIndex(Persistent):
    """Keyword index"""

    implements(IInjection, IStatistics, IIndexSearch, IKeywordQuerying)
    family = BTrees.family32

    def __init__(self, family=None):
        if family is not None:
            self.family = family
        self.clear()

    def clear(self):
        """Initialize forward and reverse mappings."""

        # The forward index maps index keywords to a sequence of docids
        self._fwd_index = self.family.OO.BTree()

        # The reverse index maps a docid to its keywords
        # TODO: Using a vocabulary might be the better choice to store
        # keywords since it would allow use to use integers instead of strings
        self._rev_index = self.family.IO.BTree()
        self._num_docs = Length(0)

    def documentCount(self):
        """Return the number of documents in the index."""
        return self._num_docs()

    def wordCount(self):
        """Return the number of indexed words"""
        return len(self._fwd_index)

    def has_doc(self, docid):
        return bool(self._rev_index.has_key(docid))

    def normalize(self, seq):
        """Perform normalization on sequence of keywords.
        
        Return normalized sequence. This method may be
        overriden by subclasses.
        
        """
        return seq

    def index_doc(self, docid, seq):
        if isinstance(seq, basestring):
            raise TypeError('seq argument must be a list/tuple of strings')
    
        if not seq:
            return

        seq = self.normalize(seq)

        old_kw = self._rev_index.get(docid, None)
        new_kw = self.family.OO.Set(seq)

        if old_kw is None:
            self._insert_forward(docid, new_kw)
            self._insert_reverse(docid, new_kw)
            self._num_docs.change(1)
        else:

            # determine added and removed keywords
            kw_added = self.family.OO.difference(new_kw, old_kw)
            kw_removed = self.family.OO.difference(old_kw, new_kw)

            # removed keywords are removed from the forward index
            for word in kw_removed:
                self._fwd_index[word].remove(docid)
            
            # now update reverse and forward indexes
            self._insert_forward(docid, kw_added)
            self._insert_reverse(docid, new_kw)
        
    def unindex_doc(self, docid):
        idx  = self._fwd_index

        try:
            for word in self._rev_index[docid]:
                idx[word].remove(docid)
                if not idx[word]:
                    del idx[word] 
        except KeyError:
            return
        
        try:
            del self._rev_index[docid]
        except KeyError:
            pass

        self._num_docs.change(-1)

    def _insert_forward(self, docid, words):
        """insert a sequence of words into the forward index """

        idx = self._fwd_index
        has_key = idx.has_key
        for word in words:
            if not has_key(word):
                idx[word] = self.family.IF.Set()
            idx[word].insert(docid)

    def _insert_reverse(self, docid, words):
        """ add words to forward index """

        if words:
            self._rev_index[docid] = words

    def search(self, query, operator='and'):
        """Execute a search given by 'query'."""
        if isinstance(query, basestring):
            query = [query]

        query = self.normalize(query)

        sets = []
        for word in query:
            docids = self._fwd_index.get(word, self.family.IF.Set())
            sets.append(docids)

        if operator == 'or':
            rs = self.family.IF.multiunion(sets)
        elif operator == 'and':
            # sort smallest to largest set so we intersect the smallest
            # number of document identifiers possible
            sets.sort(key=len)
            rs = None
            for set in sets:
                rs = self.family.IF.intersection(rs, set)
                if not rs:
                    break
        else:
            raise TypeError('Keyword index only supports `and` and `or` operators, not `%s`.' % operator)
        
        if rs:
            return rs
        else:
            return self.family.IF.Set()

    def apply(self, query):
        operator = 'and'
        if isinstance(query, dict):
            if 'operator' in query:
                operator = query.pop('operator')
            query = query['query']
        return self.search(query, operator=operator)

class CaseInsensitiveKeywordIndex(KeywordIndex):
    """A case-normalizing keyword index (for strings as keywords)"""

    def normalize(self, seq):
        return [w.lower() for w in seq]
