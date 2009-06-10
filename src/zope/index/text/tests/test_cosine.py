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
"""Text Index Tests

$Id: test_index.py 100805 2009-06-10 17:58:58Z tseaver $
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

    def test_class_conforms_to_IExtendedQuerying(self):
        from zope.interface.verify import verifyClass
        from zope.index.text.interfaces import IExtendedQuerying
        verifyClass(IExtendedQuerying, self._getTargetClass())

    def test_instance_conforms_to_IExtendedQuerying(self):
        from zope.interface.verify import verifyObject
        from zope.index.text.interfaces import IExtendedQuerying
        verifyObject(IExtendedQuerying, self._makeOne())

class CosineIndexTest32(CosineIndexTestBase, unittest.TestCase):

    def _getBTreesFamily(self):
        import BTrees
        return BTrees.family32

class CosineIndexTest64(CosineIndexTestBase, unittest.TestCase):

    def _getBTreesFamily(self):
        import BTrees
        return BTrees.family64

def test_suite():
    return unittest.TestSuite((
                      unittest.makeSuite(CosineIndexTest32),
                      unittest.makeSuite(CosineIndexTest64),
                    ))
