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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Text index.
"""
from persistent import Persistent
from zope.interface import implementer

from zope.index.interfaces import IIndexSearch
from zope.index.interfaces import IInjection
from zope.index.interfaces import IStatistics
from zope.index.text.lexicon import CaseNormalizer
from zope.index.text.lexicon import Lexicon
from zope.index.text.lexicon import Splitter
from zope.index.text.lexicon import StopWordRemover
from zope.index.text.okapiindex import OkapiIndex
from zope.index.text.queryparser import QueryParser
import six

@implementer(IInjection, IIndexSearch, IStatistics)
class TextIndex(Persistent):
    """
    Text index.

    Implements :class:`zope.index.interfaces.IInjection` and
    :class:`zope.index.interfaces.IIndexSearch`.
    """

    def __init__(self, lexicon=None, index=None):
        """Provisional constructor.

        This creates the lexicon and index if not passed in.
        """
        _explicit_lexicon = True
        if lexicon is None:
            _explicit_lexicon = False
            lexicon = Lexicon(Splitter(), CaseNormalizer(), StopWordRemover())
        if index is None:
            index = OkapiIndex(lexicon)
        self.lexicon = _explicit_lexicon and lexicon or index.lexicon
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
            if qw == 0:
                qw = 1.0

            qw *= 1.0

            for docid, score in six.iteritems(results):
                try:
                    results[docid] = score/qw
                except TypeError:
                    # We overflowed the score, perhaps wildly unlikely.
                    # Who knows.
                    results[docid] = 2**64 // 10

        return results
