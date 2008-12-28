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

from unittest import TestCase, TestSuite, main, makeSuite

import BTrees

from zope.index.keyword.index import KeywordIndex
from zope.index.interfaces import IInjection, IStatistics
from zope.index.keyword.interfaces import IKeywordQuerying
from zope.interface.verify import verifyClass

class KeywordIndexTest(TestCase):

    from BTrees.IFBTree import IFSet

    def setUp(self):
        self.index = KeywordIndex()

    def _populate_index(self):

        self.index.index_doc(1, ('zope', 'CMF', 'zope3', 'Zope3'))
        self.index.index_doc(2, ('the', 'quick', 'brown', 'FOX'))
        self.index.index_doc(3, ('Zope', 'zope'))
        self.index.index_doc(4, ())
        self.index.index_doc(5, ('cmf',))


    def _search(self, query, expected, mode='and'):

        results = self.index.search(query, mode)

        # results and expected are IFSets() but we can not
        # compare them directly since __eq__() does not seem
        # to be implemented for BTrees

        self.assertEqual(results.keys(), expected.keys())

    def _search_and(self, query, expected):
        return self._search(query, expected, 'and')

    def _search_or(self, query, expected):
        return self._search(query, expected, 'or')

    def _apply(self, query, expected, mode='and'):
        results = self.index.apply(query)
        self.assertEqual(results.keys(), expected.keys())

    def _apply_and(self, query, expected):
        results = self.index.apply({'operator': 'and', 'query': query})
        self.assertEqual(results.keys(), expected.keys())

    def _apply_or(self, query, expected):
        results = self.index.apply({'operator': 'or', 'query': query})
        self.assertEqual(results.keys(), expected.keys())

    def test_interface(self):
        verifyClass(IInjection, KeywordIndex)
        verifyClass(IStatistics, KeywordIndex)
        verifyClass(IKeywordQuerying, KeywordIndex)

    def test_empty_index(self):
        self.assertEqual(self.index.documentCount(), 0)
        self.assertEqual(self.index.wordCount(), 0)
        self._populate_index()
        self.assertEqual(self.index.documentCount(), 4)
        self.assertEqual(self.index.wordCount(), 7)
        self.index.clear()
        self.assertEqual(self.index.documentCount(), 0)
        self.assertEqual(self.index.wordCount(), 0)

    def test_unindex(self):
        self._populate_index()
        self.assertEqual(self.index.documentCount(), 4)
        self.index.unindex_doc(1)
        self.index.unindex_doc(2)
        self.assertEqual(self.index.documentCount(), 2)
        self.index.unindex_doc(-99999)     # no exception should be raised
        self.assertEqual(self.index.documentCount(), 2)

    def test_reindex(self):
        self._populate_index()
        self.assertEqual(self.index.documentCount(), 4)
        self.index.unindex_doc(1)
        self.index.unindex_doc(2)
        self.index.index_doc(1,  ('foo', 'bar', 'doom'))
        self.index.index_doc(1,  ('bar', 'blabla'))
        self.assertEqual(self.index.documentCount(), 3)
        self._search('quick',   self.IFSet())
        self._search('foo',   self.IFSet())
        self._search('bar',   self.IFSet([1]))
        self._search(['doom'],   self.IFSet())
        self._search(['blabla'],   self.IFSet([1]))
        self._search_and(('bar', 'blabla'),   self.IFSet([1]))
        self._search(['cmf'],   self.IFSet([5]))

    def test_hasdoc(self):
        self._populate_index()
        self.assertEqual(self.index.has_doc(1), 1)
        self.assertEqual(self.index.has_doc(2), 1)
        self.assertEqual(self.index.has_doc(3), 1)
        self.assertEqual(self.index.has_doc(4), 0)
        self.assertEqual(self.index.has_doc(5), 1)
        self.assertEqual(self.index.has_doc(6), 0)

    def test_simplesearch(self):
        self._populate_index()
        self._search([''],      self.IFSet())
        self._search(['cmf'],   self.IFSet([1, 5]))
        self._search(['zope'],  self.IFSet([1, 3]))
        self._search(['zope3'], self.IFSet([1]))
        self._search(['foo'],   self.IFSet())

    def test_search_and(self):
        self._populate_index()
        self._search_and(('cmf', 'zope3'), self.IFSet([1]))
        self._search_and(('cmf', 'zope'),  self.IFSet([1]))
        self._search_and(('cmf', 'zope4'), self.IFSet())
        self._search_and(('zope', 'ZOPE'), self.IFSet([1, 3]))

    def test_search_or(self):
        self._populate_index()
        self._search_or(('cmf', 'zope3'), self.IFSet([1, 5]))
        self._search_or(('cmf', 'zope'),  self.IFSet([1, 3, 5]))
        self._search_or(('cmf', 'zope4'), self.IFSet([1, 5]))
        self._search_or(('zope', 'ZOPE'), self.IFSet([1,3]))

    def test_apply(self):
        self._populate_index()
        self._apply(('cmf', 'zope3'), self.IFSet([1]))
        self._apply(('cmf', 'zope'),  self.IFSet([1]))
        self._apply(('cmf', 'zope4'), self.IFSet())
        self._apply(('zope', 'ZOPE'), self.IFSet([1, 3]))

    def test_apply_and(self):
        self._populate_index()
        self._apply_and(('cmf', 'zope3'), self.IFSet([1]))
        self._apply_and(('cmf', 'zope'),  self.IFSet([1]))
        self._apply_and(('cmf', 'zope4'), self.IFSet())
        self._apply_and(('zope', 'ZOPE'), self.IFSet([1, 3]))

    def test_apply_or(self):
        self._populate_index()
        self._apply_or(('cmf', 'zope3'), self.IFSet([1, 5]))
        self._apply_or(('cmf', 'zope'),  self.IFSet([1, 3, 5]))
        self._apply_or(('cmf', 'zope4'), self.IFSet([1, 5]))
        self._apply_or(('zope', 'ZOPE'), self.IFSet([1,3]))

    def test_index_input(self):
        self.assertRaises(
            TypeError, self.index.index_doc, 1, "non-sequence-string")


class KeywordIndexTest64(KeywordIndexTest):

    from BTrees.LFBTree import LFSet as IFSet

    def setUp(self):
        self.index = KeywordIndex(family=BTrees.family64)


def test_suite():
    return TestSuite((makeSuite(KeywordIndexTest),
                      makeSuite(KeywordIndexTest64),
                      ))

if __name__=='__main__':
    main(defaultTest='test_suite')
