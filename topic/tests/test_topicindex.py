##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from unittest import TestCase, TestSuite, main, makeSuite 

from zodb.btrees.IIBTree import IISet
from zope.index.topic.index import TopicIndex
from zope.index.topic.filter import PythonFilter
from zope.interface.verify import verifyClass

from zope.index.interfaces import ITopicFilter

class O:
    """ a dummy class """

    def __init__(self, meta_type):
        self.meta_type = meta_type

class TopicIndexTest(TestCase):

    def setUp(self):
        self.index = TopicIndex()
        self.index.addFilter(PythonFilter('doc1', "context.meta_type == 'doc1'"))
        self.index.addFilter(PythonFilter('doc2', "context.meta_type == 'doc2'"))
        self.index.addFilter(PythonFilter('doc3', "context.meta_type == 'doc3'"))

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
        verifyClass(ITopicFilter, PythonFilter)

    def testOr(self):
        self._search_or('doc1',  [1,2])
        self._search_or(['doc1'],[1,2])
        self._search_or('doc2',  [3,4]),
        self._search_or(['doc2'],[3,4])
        self._search_or(['doc1','doc2'], [1,2,3,4])

    def testAnd(self):
        self._search_and('doc1',   [1,2])
        self._search_and(['doc1'], [1,2])
        self._search_and('doc2',   [3,4])
        self._search_and(['doc2'], [3,4])
        self._search_and(['doc1','doc2'], [])


def test_suite():
    return TestSuite((makeSuite(TopicIndexTest), ))

if __name__=='__main__':
    main(defaultTest='test_suite')
