##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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

class ConformsToIQueryParseTree:

    def test_class_conforms_to_IQueryParseTree(self):
        from zope.interface.verify import verifyClass
        from zope.index.text.interfaces import IQueryParseTree
        verifyClass(IQueryParseTree, self._getTargetClass())

    def test_instance_conforms_to_IQueryParseTree(self):
        from zope.interface.verify import verifyObject
        from zope.index.text.interfaces import IQueryParseTree
        verifyObject(IQueryParseTree, self._makeOne())

class ParseTreeNodeTests(unittest.TestCase, ConformsToIQueryParseTree):

    def _getTargetClass(self):
        from zope.index.text.parsetree import ParseTreeNode
        return ParseTreeNode

    def _makeOne(self, value=None):
        if value is None:
            value = [FauxValue('XXX')]
        return self._getTargetClass()(value)

    def test_nodeType(self):
        node = self._makeOne()
        self.assertEqual(node.nodeType(), None)

    def test_getValue(self):
        value = [FauxValue('XXX')]
        node = self._makeOne(value)
        self.assertEqual(node.getValue(), value)

    def test___repr__(self):
        node = self._makeOne()
        self.assertEqual(repr(node), "ParseTreeNode([FV:XXX])")

    def test_terms(self):
        node = self._makeOne()
        self.assertEqual(list(node.terms()), ['XXX'])

    def test_executeQuery_raises(self):
        node = self._makeOne()
        self.assertRaises(NotImplementedError, node.executeQuery, FauxIndex())

class NotNodeTests(unittest.TestCase, ConformsToIQueryParseTree):

    def _getTargetClass(self):
        from zope.index.text.parsetree import NotNode
        return NotNode

    def _makeOne(self, value=None):
        if value is None:
            value = [FauxValue('XXX')]
        return self._getTargetClass()(value)

    def test_nodeType(self):
        node = self._makeOne()
        self.assertEqual(node.nodeType(), 'NOT')

    def test___repr__(self):
        node = self._makeOne()
        self.assertEqual(repr(node), "NotNode([FV:XXX])")

    def test_terms(self):
        node = self._makeOne()
        self.assertEqual(list(node.terms()), [])

    def test_executeQuery_raises(self):
        from zope.index.text.parsetree import QueryError
        node = self._makeOne()
        self.assertRaises(QueryError, node.executeQuery, FauxIndex())

class AndNodeTests(unittest.TestCase, ConformsToIQueryParseTree):

    def _getTargetClass(self):
        from zope.index.text.parsetree import AndNode
        return AndNode

    def _makeOne(self, value=None):
        if value is None:
            value = [FauxValue('XXX')]
        return self._getTargetClass()(value)

    def test_nodeType(self):
        node = self._makeOne()
        self.assertEqual(node.nodeType(), 'AND')

    def test___repr__(self):
        node = self._makeOne()
        self.assertEqual(repr(node), "AndNode([FV:XXX])")

    def test_executeQuery_no_results(self):
        from zope.index.text.parsetree import QueryError
        node = self._makeOne([FauxSubnode('FOO', None)])
        result = node.executeQuery(FauxIndex())
        self.assertEqual(dict(result), {})

class OrNodeTests(unittest.TestCase, ConformsToIQueryParseTree):

    def _getTargetClass(self):
        from zope.index.text.parsetree import AtomNode
        return AtomNode

    def _makeOne(self, value=None):
        if value is None:
            value = [FauxValue('XXX')]
        return self._getTargetClass()(value)

    def test_nodeType(self):
        node = self._makeOne()
        self.assertEqual(node.nodeType(), 'ATOM')

    def test___repr__(self):
        node = self._makeOne()
        self.assertEqual(repr(node), "AtomNode([FV:XXX])")

class AtomNodeTests(unittest.TestCase, ConformsToIQueryParseTree):

    def _getTargetClass(self):
        from zope.index.text.parsetree import AtomNode
        return AtomNode

    def _makeOne(self, value=None):
        if value is None:
            value = 'XXX'
        return self._getTargetClass()(value)

    def test_nodeType(self):
        node = self._makeOne()
        self.assertEqual(node.nodeType(), 'ATOM')

    def test___repr__(self):
        node = self._makeOne()
        self.assertEqual(repr(node), "AtomNode('XXX')")

    def test_terms(self):
        node = self._makeOne()
        self.assertEqual(node.terms(), ['XXX'])

class PhraseNodeTests(unittest.TestCase, ConformsToIQueryParseTree):

    def _getTargetClass(self):
        from zope.index.text.parsetree import PhraseNode
        return PhraseNode

    def _makeOne(self, value=None):
        if value is None:
            value = 'XXX YYY'
        return self._getTargetClass()(value)

    def test_nodeType(self):
        node = self._makeOne()
        self.assertEqual(node.nodeType(), 'PHRASE')

    def test___repr__(self):
        node = self._makeOne()
        self.assertEqual(repr(node), "PhraseNode('XXX YYY')")

    def test_executeQuery(self):
        _called_with = []
        def _search(*args, **kw):
            _called_with.append((args, kw))
            return []
        index = FauxIndex()
        index.search_phrase = _search
        node = self._makeOne()
        self.assertEqual(node.executeQuery(index), [])
        self.assertEqual(_called_with[0], (('XXX YYY',), {}))

class GlobNodeTests(unittest.TestCase, ConformsToIQueryParseTree):

    def _getTargetClass(self):
        from zope.index.text.parsetree import GlobNode
        return GlobNode

    def _makeOne(self, value=None):
        if value is None:
            value = 'XXX*'
        return self._getTargetClass()(value)

    def test_nodeType(self):
        node = self._makeOne()
        self.assertEqual(node.nodeType(), 'GLOB')

    def test___repr__(self):
        node = self._makeOne()
        self.assertEqual(repr(node), "GlobNode('XXX*')")

    def test_executeQuery(self):
        _called_with = []
        def _search(*args, **kw):
            _called_with.append((args, kw))
            return []
        index = FauxIndex()
        index.search_glob = _search
        node = self._makeOne()
        self.assertEqual(node.executeQuery(index), [])
        self.assertEqual(_called_with[0], (('XXX*',), {}))

class FauxIndex(object):

    def _get_family(self):
        import BTrees
        return BTrees.family32

    family = property(_get_family,)

class FauxValue:
    def __init__(self, *terms):
        self._terms = terms[:]
    def terms(self):
        return self._terms
    def __eq__(self, other):
        return self._terms == other._terms
    def __repr__(self):
        return 'FV:%s' % ' '.join(self._terms)


class FauxSubnode:
    def __init__(self, node_type, query_results):
        self._nodeType = node_type
        self._query_results = query_results
    def nodeType(self):
        return self._nodeType
    def executeQuery(self, index):
        return self._query_results

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ParseTreeNodeTests),
        unittest.makeSuite(NotNodeTests),
        unittest.makeSuite(AndNodeTests),
        unittest.makeSuite(OrNodeTests),
        unittest.makeSuite(AtomNodeTests),
        unittest.makeSuite(PhraseNodeTests),
        unittest.makeSuite(GlobNodeTests),
    ))
