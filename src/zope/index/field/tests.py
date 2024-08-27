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
"""Test field index
"""
import doctest
import unittest


_marker = object()


class FieldIndexTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.index.field import FieldIndex
        return FieldIndex

    def _makeOne(self, family=_marker):
        if family is _marker:
            return self._getTargetClass()()
        return self._getTargetClass()(family)

    def _populateIndex(self, index):
        index.index_doc(5, 1)  # docid, obj
        index.index_doc(2, 2)
        index.index_doc(1, 3)
        index.index_doc(3, 4)
        index.index_doc(4, 5)
        index.index_doc(8, 6)
        index.index_doc(9, 7)
        index.index_doc(7, 8)
        index.index_doc(6, 9)
        index.index_doc(11, 10)
        index.index_doc(10, 11)

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
        import BTrees
        index = self._makeOne()
        self.assertIs(index.family, BTrees.family32)
        self.assertEqual(index.documentCount(), 0)
        self.assertEqual(index.wordCount(), 0)

    def test_ctor_explicit_family(self):
        import BTrees
        index = self._makeOne(BTrees.family64)
        self.assertIs(index.family, BTrees.family64)

    def test_index_doc_new(self):
        index = self._makeOne()
        index.index_doc(1, 'value')
        self.assertEqual(index.documentCount(), 1)
        self.assertEqual(index.wordCount(), 1)
        self.assertIn(1, index._rev_index)
        self.assertIn('value', index._fwd_index)

    def test_index_doc_existing_same_value(self):
        index = self._makeOne()
        index.index_doc(1, 'value')
        index.index_doc(1, 'value')
        self.assertEqual(index.documentCount(), 1)
        self.assertEqual(index.wordCount(), 1)
        self.assertIn(1, index._rev_index)
        self.assertIn('value', index._fwd_index)
        self.assertEqual(list(index._fwd_index['value']), [1])

    def test_index_doc_existing_new_value(self):
        index = self._makeOne()
        index.index_doc(1, 'value')
        index.index_doc(1, 'new_value')
        self.assertEqual(index.documentCount(), 1)
        self.assertEqual(index.wordCount(), 1)
        self.assertIn(1, index._rev_index)
        self.assertNotIn('value', index._fwd_index)
        self.assertIn('new_value', index._fwd_index)
        self.assertEqual(list(index._fwd_index['new_value']), [1])

    def test_unindex_doc_nonesuch(self):
        index = self._makeOne()
        index.unindex_doc(1)  # doesn't raise

    def test_unindex_doc_no_residual_fwd_values(self):
        index = self._makeOne()
        index.index_doc(1, 'value')
        index.unindex_doc(1)  # doesn't raise
        self.assertEqual(index.documentCount(), 0)
        self.assertEqual(index.wordCount(), 0)
        self.assertNotIn(1, index._rev_index)
        self.assertNotIn('value', index._fwd_index)

    def test_unindex_doc_w_residual_fwd_values(self):
        index = self._makeOne()
        index.index_doc(1, 'value')
        index.index_doc(2, 'value')
        index.unindex_doc(1)  # doesn't raise
        self.assertEqual(index.documentCount(), 1)
        self.assertEqual(index.wordCount(), 1)
        self.assertNotIn(1, index._rev_index)
        self.assertIn(2, index._rev_index)
        self.assertIn('value', index._fwd_index)
        self.assertEqual(list(index._fwd_index['value']), [2])

    def test_apply_non_tuple_raises(self):
        index = self._makeOne()
        self.assertRaises(TypeError, index.apply, ['a', 'b'])

    def test_apply_empty_tuple_raises(self):
        index = self._makeOne()
        self.assertRaises(TypeError, index.apply, ('a',))

    def test_apply_one_tuple_raises(self):
        index = self._makeOne()
        self.assertRaises(TypeError, index.apply, ('a',))

    def test_apply_three_tuple_raises(self):
        index = self._makeOne()
        self.assertRaises(TypeError, index.apply, ('a', 'b', 'c'))

    def test_apply_two_tuple_miss(self):
        index = self._makeOne()
        self.assertEqual(list(index.apply(('a', 'b'))), [])

    def test_apply_two_tuple_hit(self):
        index = self._makeOne()
        index.index_doc(1, 'albatross')
        self.assertEqual(list(index.apply(('a', 'b'))), [1])

    def test_sort_w_limit_lt_1(self):
        index = self._makeOne()
        self.assertRaises(ValueError,
                          lambda: list(index.sort([1, 2, 3], limit=0)))

    def test_sort_w_empty_index(self):
        index = self._makeOne()
        self.assertEqual(list(index.sort([1, 2, 3])), [])

    def test_sort_w_empty_docids(self):
        index = self._makeOne()
        index.index_doc(1, 'albatross')
        self.assertEqual(list(index.sort([])), [])

    def test_sort_w_missing_docids(self):
        index = self._makeOne()
        index.index_doc(1, 'albatross')
        self.assertEqual(list(index.sort([2, 3])), [])

    def test_sort_force_nbest_w_missing_docids(self):
        index = self._makeOne()
        index._use_nbest = True
        index.index_doc(1, 'albatross')
        self.assertEqual(list(index.sort([2, 3])), [])

    def test_sort_force_lazy_w_missing_docids(self):
        index = self._makeOne()
        index._use_lazy = True
        index.index_doc(1, 'albatross')
        self.assertEqual(list(index.sort([2, 3])), [])

    def test_sort_lazy_nolimit(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        index._use_lazy = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1)
        self.assertEqual(list(result), [5, 2, 1, 3, 4])

    def test_sort_lazy_withlimit(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        index._use_lazy = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, limit=3)
        self.assertEqual(list(result), [5, 2, 1])

    def test_sort_nonlazy_nolimit(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1)
        self.assertEqual(list(result), [5, 2, 1, 3, 4])

    def test_sort_nonlazy_missingdocid(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5, 99])
        result = index.sort(c1)
        self.assertEqual(list(result), [5, 2, 1, 3, 4])  # 99 not present

    def test_sort_nonlazy_withlimit(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, limit=3)
        self.assertEqual(list(result), [5, 2, 1])

    def test_sort_nonlazy_reverse_nolimit(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, reverse=True)
        self.assertEqual(list(result), [4, 3, 1, 2, 5])

    def test_sort_nonlazy_reverse_withlimit(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, reverse=True, limit=3)
        self.assertEqual(list(result), [4, 3, 1])

    def test_sort_nbest(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        index._use_nbest = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, limit=3)
        self.assertEqual(list(result), [5, 2, 1])

    def test_sort_nbest_reverse(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        index._use_nbest = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, reverse=True, limit=3)
        self.assertEqual(list(result), [4, 3, 1])

    def test_sort_nbest_missing(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        index._use_nbest = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5, 99])
        result = index.sort(c1, limit=3)
        self.assertEqual(list(result), [5, 2, 1])

    def test_sort_nbest_missing_reverse(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        index._use_nbest = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5, 99])
        result = index.sort(c1, reverse=True, limit=3)
        self.assertEqual(list(result), [4, 3, 1])

    def test_sort_nodocs(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1)
        self.assertEqual(list(result), [])

    def test_sort_nodocids(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        self._populateIndex(index)
        c1 = IFSet()
        result = index.sort(c1)
        self.assertEqual(list(result), [])

    def test_sort_badlimit(self):
        from BTrees.IFBTree import IFSet
        index = self._makeOne()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, limit=0)
        self.assertRaises(ValueError, list, result)

    def test_insert_none_value_does_not_raise_typeerror(self):
        index = self._makeOne()
        index.index_doc(1, None)

    def test_insert_none_value_to_update_does_not_raise_typeerror(self):
        index = self._makeOne()
        index.index_doc(1, 5)
        index.index_doc(1, None)

    def test_insert_none_value_does_insert_into_forward_index(self):
        index = self._makeOne()
        index.index_doc(1, None)
        self.assertEqual(len(index._fwd_index), 1)
        self.assertEqual(len(index._rev_index), 1)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.rst', optionflags=doctest.ELLIPSIS),
        unittest.defaultTestLoader.loadTestsFromTestCase(FieldIndexTests),
    ))
