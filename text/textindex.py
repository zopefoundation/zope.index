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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Text index wrapper.

This exists to implement IInjection and IQuerying.

$Id$
"""

from persistent import Persistent
from zope.interface import implements

from zope.index.text.baseindex import SCALE_FACTOR
from zope.index.text.okapiindex import OkapiIndex
from zope.index.text.lexicon import Lexicon
from zope.index.text.lexicon import Splitter, CaseNormalizer, StopWordRemover
from zope.index.text.queryparser import QueryParser

from zope.index.interfaces import IInjection, IIndexSearch, IStatistics

class TextIndex(Persistent):

    implements(IInjection, IIndexSearch, IStatistics)

    def __init__(self, lexicon=None, index=None):
        """Provisional constructor.

        This creates the lexicon and index if not passed in."""
        if lexicon is None:
            lexicon = Lexicon(Splitter(), CaseNormalizer(), StopWordRemover())
        if index is None:
            index = OkapiIndex(lexicon)
        self.lexicon = lexicon
        self.index = index

    def index_doc(self, docid, text):
        self.index.index_doc(docid, text)

    def unindex_doc(self, docid):
        self.index.unindex_doc(docid)

    def clear(self):
        self.index.clear()

    def documentCount(self):
        """Return the number of documents in the index."""
        return self.index.documentCount()

    def wordCount(self):
        """Return the number of words in the index."""
        return self.index.wordCount()

    def apply(self, querytext, start=0, count=None):
        parser = QueryParser(self.lexicon)
        tree = parser.parseQuery(querytext)
        results = tree.executeQuery(self.index)
        if results:
            qw = self.index.query_weight(tree.terms())
            
            # Hack to avoid ZeroDivisionError
            if qw < SCALE_FACTOR:
                qw = SCALE_FACTOR

            # TODO we should seriously consider using float
            # scores. Since we are using ints. we'll scale this
            # result to get integers other than zero.  We'll use
            # 100 so we can pretend this is a percent. ;)
            qw *= .01

            for docid, score in results.iteritems():
                try:
                    results[docid] = int(score/qw)
                except TypeError:
                    # We overflowed the score, perhaps wildly unlikely.
                    # Who knows.
                    results[docid] = sys.maxint/10

        return results
