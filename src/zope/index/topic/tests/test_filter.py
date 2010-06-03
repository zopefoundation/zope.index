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
"""Topic Index tests
"""
import unittest

_marker = object()

class FilteredSetBaseTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.index.topic.filter import FilteredSetBase
        return FilteredSetBase

    def _makeOne(self, id=None, expr=None, family=_marker):
        if id is None:
            id = 'test'
        if expr is None:
            expr = 'True'
        if family is _marker:
            return self._getTargetClass()(id, expr)
        return self._getTargetClass()(id, expr, family)

    def test_class_conforms_to_ITopicFilteredSet(self):
        from zope.interface.verify import verifyClass
        from zope.index.topic.interfaces import ITopicFilteredSet
        verifyClass(ITopicFilteredSet, self._getTargetClass())

    def test_instance_conforms_to_ITopicFilteredSet(self):
        from zope.interface.verify import verifyObject
        from zope.index.topic.interfaces import ITopicFilteredSet
        verifyObject(ITopicFilteredSet, self._makeOne())

    def test_ctor_defaults(self):
        import BTrees
        filter = self._makeOne(family=None)
        self.failUnless(filter.family is BTrees.family32)
        self.assertEqual(filter.getId(), 'test')
        self.assertEqual(filter.getExpression(), 'True')
        self.assertEqual(len(filter.getIds()), 0)

    def test_ctor_explicit_family(self):
        import BTrees
        filter = self._makeOne(family=BTrees.family64)
        self.failUnless(filter.family is BTrees.family64)

    def test_index_doc_raises_NotImplementedError(self):
        filter = self._makeOne()
        self.assertRaises(NotImplementedError, filter.index_doc, 1, object())

    def test_unindex_doc_missing_docid(self):
        filter = self._makeOne()
        filter.unindex_doc(1) # doesn't raise
        self.assertEqual(len(filter.getIds()), 0)

    def test_unindex_doc_existing_docid(self):
        filter = self._makeOne()
        filter._ids.insert(1)
        filter.unindex_doc(1)
        self.assertEqual(len(filter.getIds()), 0)

    def test_unindex_doc_existing_docid_w_residue(self):
        filter = self._makeOne()
        filter._ids.insert(1)
        filter._ids.insert(2)
        filter.unindex_doc(1)
        self.assertEqual(len(filter.getIds()), 1)

    def test_setExpression(self):
        filter = self._makeOne()
        filter.setExpression('False')
        self.assertEqual(filter.getExpression(), 'False')

class PythonFilteredSetTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.index.topic.filter import PythonFilteredSet
        return PythonFilteredSet

    def _makeOne(self, id=None, expr=None, family=_marker):
        if id is None:
            id = 'test'
        if expr is None:
            expr = 'True'
        return self._getTargetClass()(id, expr)

    def test_index_object_expr_True(self):
        filter = self._makeOne()
        filter.index_doc(1, object())
        self.assertEqual(list(filter.getIds()), [1])

    def test_index_object_expr_False(self):
        filter = self._makeOne(expr='False')
        filter.index_doc(1, object())
        self.assertEqual(len(filter.getIds()), 0)

    def test_index_object_expr_w_zero_divide_error(self):
        filter = self._makeOne(expr='1/0')
        filter.index_doc(1, object()) # doesn't raise
        self.assertEqual(len(filter.getIds()), 0)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FilteredSetBaseTests),
        unittest.makeSuite(PythonFilteredSetTests),
    ))
