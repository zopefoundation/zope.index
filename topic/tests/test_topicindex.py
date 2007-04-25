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
"""Topic Index tests

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite 

import BTrees

from zope.index.topic.index import TopicIndex
from zope.index.topic.filter import PythonFilteredSet
from zope.interface.verify import verifyClass
from zope.interface.interface import implementedBy

class O(object):
    """ a dummy class """

    def __init__(self, meta_type):
        self.meta_type = meta_type

class TopicIndexTest(TestCase):

    family = BTrees.family32

    def setUp(self):
        self.index = TopicIndex(family=self.family)
        self.index.addFilter(
            PythonFilteredSet('doc1', "context.meta_type == 'doc1'",
                              self.family))
        self.index.addFilter(
            PythonFilteredSet('doc2', "context.meta_type == 'doc2'",
                              self.family))
        self.index.addFilter(
            PythonFilteredSet('doc3', "context.meta_type == 'doc3'",
                              self.family))

        self.index.index_doc(0 , O('doc0'))
        self.index.index_doc(1 , O('doc1'))
        self.index.index_doc(2 , O('doc1'))
        self.index.index_doc(3 , O('doc2'))
        self.index.index_doc(4 , O('doc2'))
        self.index.index_doc(5 , O('doc3'))
        self.index.index_doc(6 , O('doc3'))

    def _search(self, query, expected, operator='and'):
        
        result = self.index.search(query, operator)
        self.assertEqual(result.keys(), expected)

    def _search_or(self, query, expected):
        return self._search(query, expected, 'or')
         
    def _search_and(self, query, expected):
        return self._search(query, expected, 'and')

    def testInterfaces(self):
        for iface in implementedBy(PythonFilteredSet):
            verifyClass(iface, PythonFilteredSet)

        for iface in implementedBy(TopicIndex):
            verifyClass(iface, TopicIndex)

    def test_unindex(self):
        self.index.unindex_doc(-99)         # should not raise 
        self.index.unindex_doc(3)  
        self.index.unindex_doc(4)  
        self.index.unindex_doc(5)  
        self._search_or('doc1',  [1,2])
        self._search_or('doc2',  [])
        self._search_or('doc3',  [6])
        self._search_or('doc4',  [])

    def test_or(self):
        self._search_or('doc1',  [1,2])
        self._search_or(['doc1'],[1,2])
        self._search_or('doc2',  [3,4]),
        self._search_or(['doc2'],[3,4])
        self._search_or(['doc1','doc2'], [1,2,3,4])

    def test_and(self):
        self._search_and('doc1',   [1,2])
        self._search_and(['doc1'], [1,2])
        self._search_and('doc2',   [3,4])
        self._search_and(['doc2'], [3,4])
        self._search_and(['doc1','doc2'], [])


class TopicIndexTest64(TopicIndexTest):

    family = BTrees.family64


def test_suite():
    return TestSuite((makeSuite(TopicIndexTest),
                      makeSuite(TopicIndexTest64),
                      ))

if __name__=='__main__':
    main(defaultTest='test_suite')
