##############################################################################
#
# Copyright (c) 2002, 2009 Zope Foundation and Contributors.
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


class CosineIndexTestBase:
    # Subclasses must define '_getBTreesFamily'
    def _getTargetClass(self):
        from zope.index.text.cosineindex import CosineIndex
        return CosineIndex

    def _makeOne(self):
        from zope.index.text.lexicon import Lexicon
        from zope.index.text.lexicon import Splitter
        lexicon = Lexicon(Splitter())
        return self._getTargetClass()(lexicon, family=self._getBTreesFamily())

    def test_class_conforms_to_IInjection(self):
        from zope.interface.verify import verifyClass

        from zope.index.interfaces import IInjection
        verifyClass(IInjection, self._getTargetClass())

    def test_instance_conforms_to_IInjection(self):
        from zope.interface.verify import verifyObject

        from zope.index.interfaces import IInjection
        verifyObject(IInjection, self._makeOne())

    def test_class_conforms_to_IStatistics(self):
        from zope.interface.verify import verifyClass

        from zope.index.interfaces import IStatistics
        verifyClass(IStatistics, self._getTargetClass())

    def test_instance_conforms_to_IStatistics(self):
        from zope.interface.verify import verifyObject

        from zope.index.interfaces import IStatistics
        verifyObject(IStatistics, self._makeOne())

    def test_class_conforms_to_ILexiconBasedIndex(self):
        from zope.interface.verify import verifyClass

        from zope.index.text.interfaces import ILexiconBasedIndex
        verifyClass(ILexiconBasedIndex, self._getTargetClass())

    def test_instance_conforms_to_ILexiconBasedIndex(self):
        from zope.interface.verify import verifyObject

        from zope.index.text.interfaces import ILexiconBasedIndex
        verifyObject(ILexiconBasedIndex, self._makeOne())

    def test_class_conforms_to_IExtendedQuerying(self):
        from zope.interface.verify import verifyClass

        from zope.index.text.interfaces import IExtendedQuerying
        verifyClass(IExtendedQuerying, self._getTargetClass())

    def test_instance_conforms_to_IExtendedQuerying(self):
        from zope.interface.verify import verifyObject

        from zope.index.text.interfaces import IExtendedQuerying
        verifyObject(IExtendedQuerying, self._makeOne())

    def test__search_wids_empty_wids(self):
        index = self._makeOne()
        index.index_doc(1, 'one two three')
        self.assertEqual(index._search_wids(()), [])

    def test__search_wids_non_empty_wids(self):
        TEXT = 'one two three'
        index = self._makeOne()
        index.index_doc(1, TEXT)
        wids = [index._lexicon._wids[x] for x in TEXT.split()]
        relevances = index._search_wids(wids)
        self.assertEqual(len(relevances), len(wids))
        for relevance in relevances:
            self.assertIsInstance(relevance[0], index.family.IF.Bucket)
            self.assertEqual(len(relevance[0]), 1)
            self.assertIsInstance(relevance[0][1], float)
            self.assertIsInstance(relevance[1], float)

    def test_query_weight_empty_wids(self):
        index = self._makeOne()
        index.index_doc(1, 'one two three')
        self.assertEqual(index.query_weight(()), 0.0)

    def test_query_weight_oov_wids(self):
        index = self._makeOne()
        index.index_doc(1, 'one two three')
        self.assertEqual(index.query_weight(['nonesuch']), 0.0)

    def test_query_weight_hit_single_occurence(self):
        index = self._makeOne()
        index.index_doc(1, 'one two three')
        self.assertTrue(0.0 < index.query_weight(['one']) < 1.0)

    def test_query_weight_hit_multiple_occurences(self):
        index = self._makeOne()
        index.index_doc(1, 'one one two three one')
        self.assertTrue(0.0 < index.query_weight(['one']) < 1.0)


class CosineIndexTest32(CosineIndexTestBase, unittest.TestCase):

    def _getBTreesFamily(self):
        import BTrees
        return BTrees.family32


class CosineIndexTest64(CosineIndexTestBase, unittest.TestCase):

    def _getBTreesFamily(self):
        import BTrees
        return BTrees.family64
