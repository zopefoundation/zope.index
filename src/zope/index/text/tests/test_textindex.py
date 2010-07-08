##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Text Index Tests
"""
import unittest

_marker = object()

class TextIndexTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.index.text.textindex import TextIndex
        return TextIndex

    def _makeOne(self, lexicon=_marker, index=_marker):
        if lexicon is _marker:
            if index is _marker: # defaults
                return self._getTargetClass()()
            else:
                return self._getTargetClass()(index=index)
        else:
            if index is _marker:
                return self._getTargetClass()(lexicon)
            else:
                return self._getTargetClass()(lexicon, index)

    def _makeLexicon(self, *pipeline):
        from zope.index.text.lexicon import Lexicon
        from zope.index.text.lexicon import Splitter
        if not pipeline:
            pipeline = (Splitter(),)
        return Lexicon(*pipeline)

    def _makeOkapi(self, lexicon=None, family=None):
        import BTrees
        from zope.index.text.okapiindex import OkapiIndex
        if lexicon is None:
            lexicon = self._makeLexicon()
        if family is None:
            family = BTrees.family64
        return OkapiIndex(lexicon, family=family)

    def test_class_conforms_to_IInjection(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IInjection
        verifyClass(IInjection, self._getTargetClass())

    def test_instance_conforms_to_IInjection(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IInjection
        verifyObject(IInjection, self._makeOne())

    def test_class_conforms_to_IIndexSearch(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IIndexSearch
        verifyClass(IIndexSearch, self._getTargetClass())

    def test_instance_conforms_to_IIndexSearch(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IIndexSearch
        verifyObject(IIndexSearch, self._makeOne())

    def test_class_conforms_to_IStatistics(self):
        from zope.interface.verify import verifyClass
        from zope.index.interfaces import IStatistics
        verifyClass(IStatistics, self._getTargetClass())

    def test_instance_conforms_to_IStatistics(self):
        from zope.interface.verify import verifyObject
        from zope.index.interfaces import IStatistics
        verifyObject(IStatistics, self._makeOne())

    def test_ctor_defaults(self):
        index = self._makeOne()
        from zope.index.text.lexicon import CaseNormalizer
        from zope.index.text.lexicon import Lexicon
        from zope.index.text.lexicon import Splitter
        from zope.index.text.lexicon import StopWordRemover
        from zope.index.text.okapiindex import OkapiIndex
        self.failUnless(isinstance(index.index, OkapiIndex))
        self.failUnless(isinstance(index.lexicon, Lexicon))
        self.failUnless(index.index._lexicon is index.lexicon)
        pipeline = index.lexicon._pipeline
        self.assertEqual(len(pipeline), 3)
        self.failUnless(isinstance(pipeline[0], Splitter))
        self.failUnless(isinstance(pipeline[1], CaseNormalizer))
        self.failUnless(isinstance(pipeline[2], StopWordRemover))

    def test_ctor_explicit_lexicon(self):
        from zope.index.text.okapiindex import OkapiIndex
        lexicon = object()
        index = self._makeOne(lexicon)
        self.failUnless(index.lexicon is lexicon)
        self.failUnless(isinstance(index.index, OkapiIndex))
        self.failUnless(index.index._lexicon is lexicon)

    def test_ctor_explicit_index(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(index=okapi)
        self.failUnless(index.index is okapi)
        # See LP #232516
        self.failUnless(index.lexicon is lexicon)

    def test_ctor_explicit_lexicon_and_index(self):
        lexicon = object()
        okapi = object()
        index = self._makeOne(lexicon, okapi)
        self.failUnless(index.lexicon is lexicon)
        self.failUnless(index.index is okapi)

    def test_index_doc(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon, okapi)
        index.index_doc(1, 'cats and dogs')
        self.assertEqual(okapi._indexed[0], (1, 'cats and dogs'))

    def test_unindex_doc(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon, okapi)
        index.unindex_doc(1)
        self.assertEqual(okapi._unindexed[0], 1)

    def test_clear(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon, okapi)
        index.clear()
        self.failUnless(okapi._cleared)

    def test_documentCount(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon, okapi)
        self.assertEqual(index.documentCount(), 4)

    def test_wordCount(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon, okapi)
        self.assertEqual(index.wordCount(), 45)

    def test_apply_no_results(self):
        lexicon = DummyLexicon()
        okapi = DummyOkapi(lexicon, {})
        index = self._makeOne(lexicon, okapi)
        self.assertEqual(index.apply('anything'), {})
        self.assertEqual(okapi._query_weighted, [])
        self.assertEqual(okapi._searched, ['anything'])

    def test_apply_w_results(self):
        lexicon = DummyLexicon()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon, okapi)
        results = index.apply('anything')
        self.assertEqual(results[1], 14.0 / 42.0)
        self.assertEqual(results[2], 7.4 / 42.0)
        self.assertEqual(results[3], 3.2 / 42.0)
        self.assertEqual(okapi._query_weighted[0], ['anything'])
        self.assertEqual(okapi._searched, ['anything'])

    def test_apply_w_results_zero_query_weight(self):
        lexicon = DummyLexicon()
        okapi = DummyOkapi(lexicon)
        okapi._query_weight = 0
        index = self._makeOne(lexicon, okapi)
        results = index.apply('anything')
        self.assertEqual(results[1], 14.0)
        self.assertEqual(results[2], 7.4)
        self.assertEqual(results[3], 3.2)
        self.assertEqual(okapi._query_weighted[0], ['anything'])
        self.assertEqual(okapi._searched, ['anything'])

    def test_apply_w_results_bogus_query_weight(self):
        import sys
        DIVISOR = sys.maxint / 10
        lexicon = DummyLexicon()
        # cause TypeError in division
        okapi = DummyOkapi(lexicon, {1: '14.0', 2: '7.4', 3: '3.2'})
        index = self._makeOne(lexicon, okapi)
        results = index.apply('anything')
        self.assertEqual(results[1], DIVISOR)
        self.assertEqual(results[2], DIVISOR)
        self.assertEqual(results[3], DIVISOR)
        self.assertEqual(okapi._query_weighted[0], ['anything'])
        self.assertEqual(okapi._searched, ['anything'])

class DummyOkapi:

    _cleared = False
    _document_count = 4
    _word_count = 45
    _query_weight = 42.0

    def __init__(self, lexicon, search_results=None):
        self.lexicon = lexicon
        self._indexed = []
        self._unindexed = []
        self._searched = []
        self._query_weighted = []
        if search_results is None:
            search_results = {1: 14.0, 2: 7.4, 3: 3.2}
        self._search_results = search_results

    def index_doc(self, docid, text):
        self._indexed.append((docid, text))

    def unindex_doc(self, docid):
        self._unindexed.append(docid)

    def clear(self):
        self._cleared = True

    def documentCount(self):
        return self._document_count

    def wordCount(self):
        return self._word_count

    def query_weight(self, terms):
        self._query_weighted.append(terms)
        return self._query_weight

    def search(self, term):
        self._searched.append(term)
        return self._search_results

    search_phrase = search_glob = search

class DummyLexicon:
    def parseTerms(self, term):
        return term

def test_suite():
    return unittest.TestSuite((
                      unittest.makeSuite(TextIndexTests),
                    ))

