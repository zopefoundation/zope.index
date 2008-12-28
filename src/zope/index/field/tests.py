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
"""Test field index

$Id$
"""
import unittest
from BTrees.IFBTree import IFSet
from zope.testing import doctest

from zope.index.field import FieldIndex

class TestFieldIndexSorting(unittest.TestCase):

    def _populateIndex(self, index):
        index.index_doc(5, 1) # docid, obj
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

    def test_sort_lazy_nolimit(self):
        index = FieldIndex()
        index._use_lazy = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1)
        self.assertEqual(list(result), [5, 2, 1, 3, 4])

    def test_sort_lazy_withlimit(self):
        index = FieldIndex()
        index._use_lazy = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, limit=3)
        self.assertEqual(list(result), [5, 2, 1])

    def test_sort_nonlazy_nolimit(self):
        index = FieldIndex()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1)
        self.assertEqual(list(result), [5, 2, 1, 3, 4])

    def test_sort_nonlazy_missingdocid(self):
        index = FieldIndex()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5, 99])
        result = index.sort(c1)
        self.assertEqual(list(result), [5, 2, 1, 3, 4]) # 99 not present

    def test_sort_nonlazy_withlimit(self):
        index = FieldIndex()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, limit=3)
        self.assertEqual(list(result), [5, 2, 1])

    def test_sort_nonlazy_reverse_nolimit(self):
        index = FieldIndex()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, reverse=True)
        self.assertEqual(list(result), [4, 3, 1, 2, 5])

    def test_sort_nonlazy_reverse_withlimit(self):
        index = FieldIndex()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, reverse=True, limit=3)
        self.assertEqual(list(result), [4, 3, 1])

    def test_sort_nbest(self):
        index = FieldIndex()
        index._use_nbest = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, limit=3)
        self.assertEqual(list(result), [5, 2, 1])

    def test_sort_nbest_reverse(self):
        index = FieldIndex()
        index._use_nbest = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, reverse=True, limit=3)
        self.assertEqual(list(result), [4, 3, 1])

    def test_sort_nbest_missing(self):
        index = FieldIndex()
        index._use_nbest = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5, 99])
        result = index.sort(c1, limit=3)
        self.assertEqual(list(result), [5, 2, 1])

    def test_sort_nbest_missing_reverse(self):
        index = FieldIndex()
        index._use_nbest = True
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5, 99])
        result = index.sort(c1, reverse=True, limit=3)
        self.assertEqual(list(result), [4, 3, 1])

    def test_sort_nodocs(self):
        index = FieldIndex()
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1)
        self.assertEqual(list(result), [])

    def test_sort_nodocids(self):
        index = FieldIndex()
        self._populateIndex(index)
        c1 = IFSet()
        result = index.sort(c1)
        self.assertEqual(list(result), [])

    def test_sort_badlimit(self):
        index = FieldIndex()
        self._populateIndex(index)
        c1 = IFSet([1, 2, 3, 4, 5])
        result = index.sort(c1, limit=0)
        self.assertRaises(ValueError, list, result)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt', optionflags=doctest.ELLIPSIS),
        unittest.makeSuite(TestFieldIndexSorting),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
