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
"""Query Engine tests

$Id$
"""
import unittest

import BTrees

from zope.index.text.queryparser import QueryParser
from zope.index.text.parsetree import QueryError
from zope.index.text.lexicon import Lexicon, Splitter

class FauxIndex(object):

    family = BTrees.family32

    def search(self, term):
        b = self.family.IF.Bucket()
        if term == "foo":
            b[1] = b[3] = 1
        elif term == "bar":
            b[1] = b[2] = 1
        elif term == "ham":
            b[1] = b[2] = b[3] = b[4] = 1
        return b

class TestQueryEngine(unittest.TestCase):

    def setUp(self):
        self.lexicon = Lexicon(Splitter())
        self.parser = QueryParser(self.lexicon)
        self.index = FauxIndex()

    def compareSet(self, set, dict):
        d = {}
        for k, v in set.items():
            d[k] = v
        self.assertEqual(d, dict)

    def compareQuery(self, query, dict):
        tree = self.parser.parseQuery(query)
        set = tree.executeQuery(self.index)
        self.compareSet(set, dict)

    def testExecuteQuery(self):
        self.compareQuery("foo AND bar", {1: 2})
        self.compareQuery("foo OR bar", {1: 2, 2: 1, 3:1})
        self.compareQuery("foo AND NOT bar", {3: 1})
        self.compareQuery("foo AND foo AND foo", {1: 3, 3: 3})
        self.compareQuery("foo OR foo OR foo", {1: 3, 3: 3})
        self.compareQuery("ham AND NOT foo AND NOT bar", {4: 1})
        self.compareQuery("ham OR foo OR bar", {1: 3, 2: 2, 3: 2, 4: 1})
        self.compareQuery("ham AND foo AND bar", {1: 3})

    def testInvalidQuery(self):
        from zope.index.text.parsetree import NotNode, AtomNode
        tree = NotNode(AtomNode("foo"))
        self.assertRaises(QueryError, tree.executeQuery, self.index)

def test_suite():
    return unittest.makeSuite(TestQueryEngine)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
