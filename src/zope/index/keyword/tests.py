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

import unittest

class _KeywordIndexTestsBase:

    def _getTargetClass(self):
        from zope.index.keyword.index import KeywordIndex
        return KeywordIndex

    def _populate(self, index):

        index.index_doc(1, ('zope', 'CMF', 'Zope3'))
        index.index_doc(2, ('the', 'quick', 'brown', 'FOX'))
        index.index_doc(3, ('Zope',))
        index.index_doc(4, ())
        index.index_doc(5, ('cmf',))

    _populated_doc_count = 4
    _populated_word_count = 9

    def test_normalize(self):
        index = self._makeOne()
        self.assertEqual(index.normalize(['Foo']), ['Foo'])

    def test_simplesearch(self):
        index = self._makeOne()
        self._populate(index)
        self._search(index, [''],      self.IFSet())
        self._search(index, 'cmf',     self.IFSet([5]))
        self._search(index, ['cmf'],   self.IFSet([5]))
        self._search(index, ['Zope'],  self.IFSet([3]))
        self._search(index, ['Zope3'], self.IFSet([1]))
        self._search(index, ['foo'],   self.IFSet())

    def test_search_and(self):
        index = self._makeOne()
        self._populate(index)
        self._search_and(index, ('CMF', 'Zope3'), self.IFSet([1]))
        self._search_and(index, ('CMF', 'zope'),  self.IFSet([1]))
        self._search_and(index, ('cmf', 'zope4'), self.IFSet())
        self._search_and(index, ('quick', 'FOX'), self.IFSet([2]))

    def test_search_or(self):
        index = self._makeOne()
        self._populate(index)
        self._search_or(index, ('cmf', 'Zope3'), self.IFSet([1, 5]))
        self._search_or(index, ('cmf', 'zope'),  self.IFSet([1, 5]))
        self._search_or(index, ('cmf', 'zope4'), self.IFSet([5]))
        self._search_or(index, ('zope', 'Zope'), self.IFSet([1,3]))

    def test_apply(self):
        index = self._makeOne()
        self._populate(index)
        self._apply(index, ('CMF', 'Zope3'), self.IFSet([1]))
        self._apply(index, ('CMF', 'zope'),  self.IFSet([1]))
        self._apply(index, ('cmf', 'zope4'), self.IFSet())
        self._apply(index, ('quick', 'FOX'), self.IFSet([2]))

    def test_apply_and(self):
        index = self._makeOne()
        self._populate(index)
        self._apply_and(index, ('CMF', 'Zope3'), self.IFSet([1]))
        self._apply_and(index, ('CMF', 'zope'),  self.IFSet([1]))
        self._apply_and(index, ('cmf', 'zope4'), self.IFSet())
        self._apply_and(index, ('quick', 'FOX'), self.IFSet([2]))

    def test_apply_or(self):
        index = self._makeOne()
        self._populate(index)
        self._apply_or(index, ('cmf', 'Zope3'), self.IFSet([1, 5]))
        self._apply_or(index, ('cmf', 'zope'),  self.IFSet([1, 5]))
        self._apply_or(index, ('cmf', 'zope4'), self.IFSet([5]))
        self._apply_or(index, ('zope', 'Zope'), self.IFSet([1,3]))

    def test_apply_with_only_tree_set(self):
        index = self._makeOne()
        index.tree_threshold = 0
        self._populate(index)
        self.assertEqual(type(index._fwd_index['zope']),
            type(self.IFTreeSet()))
        self._apply_and(index, ('CMF', 'Zope3'), self.IFSet([1]))
        self._apply_and(index, ('CMF', 'zope'),  self.IFSet([1]))
        self._apply_and(index, ('cmf', 'zope4'), self.IFSet())
        self._apply_and(index, ('quick', 'FOX'), self.IFSet([2]))

    def test_apply_with_mix_of_tree_set_and_simple_set(self):
        index = self._makeOne()
        index.tree_threshold = 2
        self._populate(index)
        self.assertEqual(type(index._fwd_index['zope']),
            type(self.IFSet()))
        self._apply_and(index, ('CMF', 'Zope3'), self.IFSet([1]))
        self._apply_and(index, ('CMF', 'zope'),  self.IFSet([1]))
        self._apply_and(index, ('cmf', 'zope4'), self.IFSet())
        self._apply_and(index, ('quick', 'FOX'), self.IFSet([2]))

    def test_optimize_converts_to_tree_set(self):
        index = self._makeOne()
        self._populate(index)
        self.assertEqual(type(index._fwd_index['zope']),
            type(self.IFSet()))
        index.tree_threshold = 0
        index.optimize()
        self.assertEqual(type(index._fwd_index['zope']),
            type(self.IFTreeSet()))

    def test_optimize_converts_to_simple_set(self):
        index = self._makeOne()
        index.tree_threshold = 0
        self._populate(index)
        self.assertEqual(type(index._fwd_index['zope']),
            type(self.IFTreeSet()))
        index.tree_threshold = 99
        index.optimize()
        self.assertEqual(type(index._fwd_index['zope']),
            type(self.IFSet()))

    def test_optimize_leaves_words_alone(self):
        index = self._makeOne()
        self._populate(index)
        self.assertEqual(type(index._fwd_index['zope']),
            type(self.IFSet()))
        index.tree_threshold = 99
        index.optimize()
        self.assertEqual(type(index._fwd_index['zope']),
            type(self.IFSet()))

    def test_index_with_empty_sequence_unindexes(self):
        index = self._makeOne()
        self._populate(index)
        self._search(index, 'cmf', self.IFSet([5]))
        index.index_doc(5, ())
        self._search(index, 'cmf', self.IFSet([]))


class CaseInsensitiveKeywordIndexTestsBase:

    def _getTargetClass(self):
        from zope.index.keyword.index import CaseInsensitiveKeywordIndex
        return CaseInsensitiveKeywordIndex

    def _populate(self, index):

        index.index_doc(1, ('zope', 'CMF', 'zope3', 'Zope3'))
        index.index_doc(2, ('the', 'quick', 'brown', 'FOX'))
        index.index_doc(3, ('Zope', 'zope'))
        index.index_doc(4, ())
        index.index_doc(5, ('cmf',))

    _populated_doc_count = 4
    _populated_word_count = 7

    def test_normalize(self):
        index = self._makeOne()
        self.assertEqual(index.normalize(['Foo']), ['foo'])

    def test_simplesearch(self):
        index = self._makeOne()
        self._populate(index)
        self._search(index, [''],      self.IFSet())
        self._search(index, 'cmf',     self.IFSet([1, 5]))
        self._search(index, ['cmf'],   self.IFSet([1, 5]))
        self._search(index, ['zope'],  self.IFSet([1, 3]))
        self._search(index, ['zope3'], self.IFSet([1]))
        self._search(index, ['foo'],   self.IFSet())

    def test_search_and(self):
        index = self._makeOne()
        self._populate(index)
        self._search_and(index, ('cmf', 'zope3'), self.IFSet([1]))
        self._search_and(index, ('cmf', 'zope'),  self.IFSet([1]))
        self._search_and(index, ('cmf', 'zope4'), self.IFSet())
        self._search_and(index, ('zope', 'ZOPE'), self.IFSet([1, 3]))

    def test_search_or(self):
        index = self._makeOne()
        self._populate(index)
        self._search_or(index, ('cmf', 'zope3'), self.IFSet([1, 5]))
        self._search_or(index, ('cmf', 'zope'),  self.IFSet([1, 3, 5]))
        self._search_or(index, ('cmf', 'zope4'), self.IFSet([1, 5]))
        self._search_or(index, ('zope', 'ZOPE'), self.IFSet([1,3]))

    def test_apply(self):
        index = self._makeOne()
        self._populate(index)
        self._apply(index, ('cmf', 'zope3'), self.IFSet([1]))
        self._apply(index, ('cmf', 'zope'),  self.IFSet([1]))
        self._apply(index, ('cmf', 'zope4'), self.IFSet())
        self._apply(index, ('zope', 'ZOPE'), self.IFSet([1, 3]))

    def test_apply_and(self):
        index = self._makeOne()
        self._populate(index)
        self._apply_and(index, ('cmf', 'zope3'), self.IFSet([1]))
        self._apply_and(index, ('cmf', 'zope'),  self.IFSet([1]))
        self._apply_and(index, ('cmf', 'zope4'), self.IFSet())
        self._apply_and(index, ('zope', 'ZOPE'), self.IFSet([1, 3]))

    def test_apply_or(self):
        index = self._makeOne()
        self._populate(index)
        self._apply_or(index, ('cmf', 'zope3'), self.IFSet([1, 5]))
        self._apply_or(index, ('cmf', 'zope'),  self.IFSet([1, 3, 5]))
        self._apply_or(index, ('cmf', 'zope4'), self.IFSet([1, 5]))
        self._apply_or(index, ('zope', 'ZOPE'), self.IFSet([1,3]))

class _ThirtyTwoBitBase:

    def _get_family(self):
        import BTrees
        return BTrees.family32

    def IFSet(self, *args, **kw):
        from BTrees.IFBTree import IFSet
        return IFSet(*args, **kw)

    def IFTreeSet(self, *args, **kw):
        from BTrees.IFBTree import IFTreeSet
        return IFTreeSet(*args, **kw)

class _SixtyFourBitBase:

    def _get_family(self):
        import BTrees
        return BTrees.family64

    def IFSet(self, *args, **kw):
        from BTrees.LFBTree import LFSet
        return LFSet(*args, **kw)

    def IFTreeSet(self, *args, **kw):
        from BTrees.LFBTree import LFTreeSet
        return LFTreeSet(*args, **kw)

_marker = object()

class _TestCaseBase:

    def _makeOne(self, family=_marker):
        if family is _marker:
            return self._getTargetClass()(self._get_family())
        return self._getTargetClass()(family)

    def _search(self, index, query, expected, mode='and'):
        results = index.search(query, mode)

        # results and expected are IFSets() but we can not
        # compare them directly since __eq__() does not seem
        # to be implemented for BTrees
        self.assertEqual(results.keys(), expected.keys())

    def _search_and(self, index, query, expected):
        return self._search(index, query, expected, 'and')

    def _search_or(self, index, query, expected):
        return self._search(index, query, expected, 'or')

    def _apply(self, index, query, expected, mode='and'):
        results = index.apply(query)
        self.assertEqual(results.keys(), expected.keys())

    def _apply_and(self, index, query, expected):
        results = index.apply({'operator': 'and', 'query': query})
        self.assertEqual(results.keys(), expected.keys())

    def _apply_or(self, index, query, expected):
        results = index.apply({'operator': 'or', 'query': query})
        self.assertEqual(results.keys(), expected.keys())

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

    def test_class_conforms_to_IKeywordQuerying(self):
        from zope.interface.verify import verifyClass
        from zope.index.keyword.interfaces import IKeywordQuerying
        verifyClass(IKeywordQuerying, self._getTargetClass())

    def test_instance_conforms_to_IKeywordQuerying(self):
        from zope.interface.verify import verifyObject
        from zope.index.keyword.interfaces import IKeywordQuerying
        verifyObject(IKeywordQuerying, self._makeOne())

    def test_ctor_defaults(self):
        index = self._makeOne()
        self.assertTrue(index.family is self._get_family())

    def test_ctor_explicit_family(self):
        import BTrees
        index = self._makeOne(family=BTrees.family64)
        self.assertTrue(index.family is BTrees.family64)

    def test_empty_index(self):
        index = self._makeOne()
        self.assertEqual(index.documentCount(), 0)
        self.assertEqual(index.wordCount(), 0)
        self.assertFalse(index.has_doc(1))

    def test_index_doc_string_value_raises(self):
        index = self._makeOne()
        self.assertRaises(TypeError, index.index_doc, 1, 'albatross')

    def test_index_doc_single(self):
        index = self._makeOne()
        index.index_doc(1, ('albatross', 'cormorant'))
        self.assertEqual(index.documentCount(), 1)
        self.assertEqual(index.wordCount(), 2)
        self.assertTrue(index.has_doc(1))
        self.assertTrue('albatross' in index._fwd_index)
        self.assertTrue('cormorant' in index._fwd_index)

    def test_index_doc_existing(self):
        index = self._makeOne()
        index.index_doc(1, ('albatross', 'cormorant'))
        index.index_doc(1, ('buzzard', 'cormorant'))
        self.assertEqual(index.documentCount(), 1)
        self.assertEqual(index.wordCount(), 2)
        self.assertTrue(index.has_doc(1))
        self.assertFalse('albatross' in index._fwd_index)
        self.assertTrue('buzzard' in index._fwd_index)
        self.assertTrue('cormorant' in index._fwd_index)

    def test_index_doc_many(self):
        index = self._makeOne()
        self._populate(index)
        self.assertEqual(index.documentCount(), self._populated_doc_count)
        self.assertEqual(index.wordCount(), self._populated_word_count)
        for docid in range(1, 6):
            if docid == 4:
                self.assertFalse(index.has_doc(docid))
            else:
                self.assertTrue(index.has_doc(docid))

    def test_clear(self):
        index = self._makeOne()
        self._populate(index)
        index.clear()
        self.assertEqual(index.documentCount(), 0)
        self.assertEqual(index.wordCount(), 0)
        for docid in range(1, 6):
            self.assertFalse(index.has_doc(docid))

    def test_unindex_doc_missing(self):
        index = self._makeOne()
        index.unindex_doc(1) # doesn't raise

    def test_unindex_no_residue(self):
        index = self._makeOne()
        index.index_doc(1, ('albatross', ))
        index.unindex_doc(1)
        self.assertEqual(index.documentCount(), 0)
        self.assertEqual(index.wordCount(), 0)
        self.assertFalse(index.has_doc(1))

    def test_unindex_w_residue(self):
        index = self._makeOne()
        index.index_doc(1, ('albatross', ))
        index.index_doc(2, ('albatross', 'cormorant'))
        index.unindex_doc(1)
        self.assertEqual(index.documentCount(), 1)
        self.assertEqual(index.wordCount(), 2)
        self.assertFalse(index.has_doc(1))

    def test_hasdoc(self):
        index = self._makeOne()
        self._populate(index)
        self.assertEqual(index.has_doc(1), 1)
        self.assertEqual(index.has_doc(2), 1)
        self.assertEqual(index.has_doc(3), 1)
        self.assertEqual(index.has_doc(4), 0)
        self.assertEqual(index.has_doc(5), 1)
        self.assertEqual(index.has_doc(6), 0)

    def test_search_bad_operator(self):
        index = self._makeOne()
        self.assertRaises(TypeError, index.search, 'whatever', 'maybe')


class KeywordIndexTests32(_KeywordIndexTestsBase,
                          _ThirtyTwoBitBase,
                          _TestCaseBase,
                          unittest.TestCase):
    pass

class CaseInsensitiveKeywordIndexTests32(CaseInsensitiveKeywordIndexTestsBase,
                                         _ThirtyTwoBitBase,
                                         _TestCaseBase,
                                         unittest.TestCase):
    pass

class KeywordIndexTests64(_KeywordIndexTestsBase,
                          _SixtyFourBitBase,
                          _TestCaseBase,
                          unittest.TestCase):
    pass

class CaseInsensitiveKeywordIndexTests64(CaseInsensitiveKeywordIndexTestsBase,
                                         _SixtyFourBitBase,
                                         _TestCaseBase,
                                         unittest.TestCase):
    pass



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(KeywordIndexTests32),
        unittest.makeSuite(KeywordIndexTests64),
        unittest.makeSuite(CaseInsensitiveKeywordIndexTests32),
        unittest.makeSuite(CaseInsensitiveKeywordIndexTests64),
    ))
