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
"""Topic Index tests
"""
import unittest

# pylint:disable=protected-access,blacklisted-name

_marker = object()

class TopicIndexTest(unittest.TestCase):

    def _getTargetClass(self):
        from zope.index.topic.index import TopicIndex
        return TopicIndex

    def _get_family(self):
        import BTrees
        return BTrees.family32

    def _makeOne(self, family=_marker, populate=False):
        if family is _marker:
            family = self._get_family()
        if family is None:
            index = self._getTargetClass()()
        index = self._getTargetClass()(family)
        if populate:
            self._addFilters(index)
            self._populate(index)
        return index

    def _search(self, index, query, expected, operator='and'):
        result = index.search(query, operator)
        self.assertEqual(result.keys(), expected)

    def _search_or(self, index, query, expected):
        return self._search(index, query, expected, 'or')

    def _search_and(self, index, query, expected):
        return self._search(index, query, expected, 'and')

    def _apply(self, index, query, expected, operator='and'):
        result = index.apply(query)
        self.assertEqual(result.keys(), expected)

    def _apply_or(self, index, query, expected):
        result = index.apply({'query': query, 'operator': 'or'})
        self.assertEqual(result.keys(), expected)

    def _apply_and(self, index, query, expected):
        result = index.apply({'query': query, 'operator': 'and'})
        self.assertEqual(result.keys(), expected)

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

    def test_class_conforms_to_ITopicQuerying(self):
        from zope.interface.verify import verifyClass
        from zope.index.topic.interfaces import ITopicQuerying
        verifyClass(ITopicQuerying, self._getTargetClass())

    def test_instance_conforms_to_ITopicQuerying(self):
        from zope.interface.verify import verifyObject
        from zope.index.topic.interfaces import ITopicQuerying
        verifyObject(ITopicQuerying, self._makeOne())

    def test_ctor_defaults(self):
        import BTrees
        index = self._makeOne(family=None)
        self.assertTrue(index.family is BTrees.family32)

    def test_ctor_explicit_family(self):
        import BTrees
        index = self._makeOne(family=BTrees.family64)
        self.assertTrue(index.family is BTrees.family64)

    def test_clear_erases_filters(self):
        index = self._makeOne()
        foo = DummyFilter('foo')
        index.addFilter(foo)
        index.clear()
        self.assertEqual(list(index._filters), [])

    def test_addFilter(self):
        index = self._makeOne()
        foo = DummyFilter('foo')
        index.addFilter(foo)
        self.assertEqual(list(index._filters), ['foo'])
        self.assertTrue(index._filters['foo'] is foo)

    def test_addFilter_duplicate_replaces(self):
        index = self._makeOne()
        foo = DummyFilter('foo')
        index.addFilter(foo)
        foo2 = DummyFilter('foo')
        index.addFilter(foo2)
        self.assertEqual(list(index._filters), ['foo'])
        self.assertTrue(index._filters['foo'] is foo2)

    def test_delFilter_nonesuch_raises_KeyError(self):
        index = self._makeOne()
        self.assertRaises(KeyError, index.delFilter, 'nonesuch')

    def test_delFilter(self):
        index = self._makeOne()
        foo = DummyFilter('foo')
        index.addFilter(foo)
        bar = DummyFilter('bar')
        index.addFilter(bar)
        index.delFilter('foo')
        self.assertEqual(list(index._filters), ['bar'])
        self.assertTrue(index._filters['bar'] is bar)

    def test_clearFilters_empty(self):
        index = self._makeOne()
        index.clearFilters() # doesn't raise

    def test_clearFilters_non_empty(self):
        index = self._makeOne()
        foo = DummyFilter('foo')
        index.addFilter(foo)
        bar = DummyFilter('bar')
        index.addFilter(bar)
        index.clearFilters()
        self.assertTrue(foo._cleared)
        self.assertTrue(bar._cleared)

    def test_index_doc(self):
        index = self._makeOne()
        foo = DummyFilter('foo')
        index.addFilter(foo)
        bar = DummyFilter('bar')
        index.addFilter(bar)
        obj = object()
        index.index_doc(1, obj)
        self.assertEqual(foo._indexed, [(1, obj)])
        self.assertEqual(bar._indexed, [(1, obj)])

    def test_unindex_doc(self):
        index = self._makeOne()
        foo = DummyFilter('foo')
        index.addFilter(foo)
        bar = DummyFilter('bar')
        index.addFilter(bar)
        index.unindex_doc(1)
        self.assertEqual(foo._unindexed, [1])
        self.assertEqual(bar._unindexed, [1])

    def test_search_non_tuple_list_query(self):
        index = self._makeOne()
        self.assertRaises(TypeError, index.search, {'nonesuch': 'ugh'})

    def test_search_bad_operator(self):
        index = self._makeOne()
        self.assertRaises(TypeError, index.search, ['whatever'], 'maybe')

    def test_search_no_filters_list_query(self):
        index = self._makeOne()
        result = index.search(['nonesuch'])
        self.assertEqual(set(result), set())

    def test_search_no_filters_tuple_query(self):
        index = self._makeOne()
        result = index.search(('nonesuch',))
        self.assertEqual(set(result), set())

    def test_search_no_filters_string_query(self):
        index = self._makeOne()
        result = index.search('nonesuch')
        self.assertEqual(set(result), set())

    def test_search_query_matches_one_filter(self):
        index = self._makeOne()
        foo = DummyFilter('foo', [1, 2, 3], self._get_family())
        index.addFilter(foo)
        bar = DummyFilter('bar', [2, 3, 4], self._get_family())
        index.addFilter(bar)
        result = index.search(['foo'])
        self.assertEqual(set(result), set([1, 2, 3]))

    def test_search_query_matches_multiple_implicit_operator(self):
        index = self._makeOne()
        foo = DummyFilter('foo', [1, 2, 3], self._get_family())
        index.addFilter(foo)
        bar = DummyFilter('bar', [2, 3, 4], self._get_family())
        index.addFilter(bar)
        result = index.search(['foo', 'bar'])
        self.assertEqual(set(result), set([2, 3]))

    def test_search_query_matches_multiple_implicit_op_no_intersect(self):
        index = self._makeOne()
        foo = DummyFilter('foo', [1, 2, 3], self._get_family())
        index.addFilter(foo)
        bar = DummyFilter('bar', [4, 5, 6], self._get_family())
        index.addFilter(bar)
        result = index.search(['foo', 'bar'])
        self.assertEqual(set(result), set())

    def test_search_query_matches_multiple_explicit_and(self):
        index = self._makeOne()
        foo = DummyFilter('foo', [1, 2, 3], self._get_family())
        index.addFilter(foo)
        bar = DummyFilter('bar', [2, 3, 4], self._get_family())
        index.addFilter(bar)
        result = index.search(['foo', 'bar'], operator='and')
        self.assertEqual(set(result), set([2, 3]))

    def test_search_query_matches_multiple_explicit_or(self):
        index = self._makeOne()
        foo = DummyFilter('foo', [1, 2, 3], self._get_family())
        index.addFilter(foo)
        bar = DummyFilter('bar', [2, 3, 4], self._get_family())
        index.addFilter(bar)
        result = index.search(['foo', 'bar'], operator='or')
        self.assertEqual(set(result), set([1, 2, 3, 4]))

    def test_apply_query_matches_multiple_non_dict_query(self):
        index = self._makeOne()
        foo = DummyFilter('foo', [1, 2, 3], self._get_family())
        index.addFilter(foo)
        bar = DummyFilter('bar', [2, 3, 4], self._get_family())
        index.addFilter(bar)
        result = index.apply(['foo', 'bar'])
        self.assertEqual(set(result), set([2, 3]))

    def test_apply_query_matches_multiple_implicit_op(self):
        index = self._makeOne()
        foo = DummyFilter('foo', [1, 2, 3], self._get_family())
        index.addFilter(foo)
        bar = DummyFilter('bar', [2, 3, 4], self._get_family())
        index.addFilter(bar)
        result = index.apply({'query': ['foo', 'bar']})
        self.assertEqual(set(result), set([2, 3]))

    def test_apply_query_matches_multiple_explicit_and(self):
        index = self._makeOne()
        foo = DummyFilter('foo', [1, 2, 3], self._get_family())
        index.addFilter(foo)
        bar = DummyFilter('bar', [2, 3, 4], self._get_family())
        index.addFilter(bar)
        result = index.apply({'query': ['foo', 'bar'], 'operator': 'and'})
        self.assertEqual(set(result), set([2, 3]))

    def test_apply_query_matches_multiple_explicit_or(self):
        index = self._makeOne()
        foo = DummyFilter('foo', [1, 2, 3], self._get_family())
        index.addFilter(foo)
        bar = DummyFilter('bar', [2, 3, 4], self._get_family())
        index.addFilter(bar)
        result = index.apply({'query': ['foo', 'bar'], 'operator': 'or'})
        self.assertEqual(set(result), set([1, 2, 3, 4]))

    def _addFilters(self, index):
        from zope.index.topic.filter import PythonFilteredSet
        index.addFilter(
            PythonFilteredSet('doc1', "context.meta_type == 'doc1'",
                              index.family))
        index.addFilter(
            PythonFilteredSet('doc2', "context.meta_type == 'doc2'",
                              index.family))
        index.addFilter(
            PythonFilteredSet('doc3', "context.meta_type == 'doc3'",
                              index.family))

    def _populate(self, index):

        class O(object):
            """ a dummy class """

            def __init__(self, meta_type):
                self.meta_type = meta_type

        index.index_doc(0, O('doc0'))
        index.index_doc(1, O('doc1'))
        index.index_doc(2, O('doc1'))
        index.index_doc(3, O('doc2'))
        index.index_doc(4, O('doc2'))
        index.index_doc(5, O('doc3'))
        index.index_doc(6, O('doc3'))

    def test_unindex(self):
        index = self._makeOne(populate=True)
        index.unindex_doc(-99)         # should not raise
        index.unindex_doc(3)
        index.unindex_doc(4)
        index.unindex_doc(5)
        self._search_or(index, 'doc1', [1, 2])
        self._search_or(index, 'doc2', [])
        self._search_or(index, 'doc3', [6])
        self._search_or(index, 'doc4', [])

    def test_or(self):
        index = self._makeOne(populate=True)
        self._search_or(index, 'doc1', [1, 2])
        self._search_or(index, ['doc1'], [1, 2])
        self._search_or(index, 'doc2', [3, 4])
        self._search_or(index, ['doc2'], [3, 4])
        self._search_or(index, ['doc1', 'doc2'], [1, 2, 3, 4])

    def test_and(self):
        index = self._makeOne(populate=True)
        self._search_and(index, 'doc1', [1, 2])
        self._search_and(index, ['doc1'], [1, 2])
        self._search_and(index, 'doc2', [3, 4])
        self._search_and(index, ['doc2'], [3, 4])
        self._search_and(index, ['doc1', 'doc2'], [])

    def test_apply_or(self):
        index = self._makeOne(populate=True)
        self._apply_or(index, 'doc1', [1, 2])
        self._apply_or(index, ['doc1'], [1, 2])
        self._apply_or(index, 'doc2', [3, 4])
        self._apply_or(index, ['doc2'], [3, 4])
        self._apply_or(index, ['doc1', 'doc2'], [1, 2, 3, 4])

    def test_apply_and(self):
        index = self._makeOne(populate=True)
        self._apply_and(index, 'doc1', [1, 2])
        self._apply_and(index, ['doc1'], [1, 2])
        self._apply_and(index, 'doc2', [3, 4])
        self._apply_and(index, ['doc2'], [3, 4])
        self._apply_and(index, ['doc1', 'doc2'], [])

    def test_apply(self):
        index = self._makeOne(populate=True)
        self._apply(index, 'doc1', [1, 2])
        self._apply(index, ['doc1'], [1, 2])
        self._apply(index, 'doc2', [3, 4])
        self._apply(index, ['doc2'], [3, 4])
        self._apply(index, ['doc1', 'doc2'], [])

class TopicIndexTest64(TopicIndexTest):

    def _get_family(self):
        import BTrees
        return BTrees.family64


class DummyFilter(object):

    _cleared = False

    def __init__(self, id, ids=(), family=None):
        self._id = id
        self._indexed = []
        self._unindexed = []
        self._family = family
        self._ids = ids

    def getId(self):
        return self._id

    def clear(self):
        self._cleared = True

    def index_doc(self, docid, obj):
        self._indexed.append((docid, obj))

    def unindex_doc(self, docid):
        self._unindexed.append(docid)

    def getIds(self):
        assert self._family is not None
        return self._family.IF.TreeSet(self._ids)
