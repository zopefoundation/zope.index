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
"""Generic parser support: exception and parse tree nodes.
"""
from zope.interface import implementer

from zope.index.text.interfaces import IQueryParseTree
from zope.index.text.setops import mass_weightedIntersection
from zope.index.text.setops import mass_weightedUnion


class QueryError(Exception):
    pass


class ParseError(Exception):
    pass


@implementer(IQueryParseTree)
class ParseTreeNode:

    _nodeType = None

    def __init__(self, value):
        self._value = value

    def nodeType(self):
        return self._nodeType

    def getValue(self):
        return self._value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.getValue()!r})"

    def terms(self):
        t = []
        for v in self.getValue():
            t.extend(v.terms())
        return t

    def executeQuery(self, index):
        raise NotImplementedError


class NotNode(ParseTreeNode):

    _nodeType = "NOT"

    def terms(self):
        return []

    def executeQuery(self, index):
        raise QueryError("NOT parse tree node cannot be executed directly")


class AndNode(ParseTreeNode):

    _nodeType = "AND"

    def executeQuery(self, index):
        L = []
        Nots = []
        for subnode in self.getValue():
            if subnode.nodeType() == "NOT":
                r = subnode.getValue().executeQuery(index)
                # If None, technically it matches every doc, but we treat
                # it as if it matched none (we want
                #     real_word AND NOT stop_word
                # to act like plain real_word).
                if r is not None:
                    Nots.append((r, 1))
            else:
                r = subnode.executeQuery(index)
                # If None, technically it matches every doc, so needn't be
                # included.
                if r is not None:
                    L.append((r, 1))
        set = mass_weightedIntersection(L, index.family)
        if Nots:
            notset = mass_weightedUnion(Nots, index.family)
            set = index.family.IF.difference(set, notset)
        return set


class OrNode(ParseTreeNode):

    _nodeType = "OR"

    def executeQuery(self, index):
        weighted = []
        for node in self.getValue():
            r = node.executeQuery(index)
            # If None, technically it matches every doc, but we treat
            # it as if it matched none (we want
            #     real_word OR stop_word
            # to act like plain real_word).
            if r is not None:
                weighted.append((r, 1))
        return mass_weightedUnion(weighted, index.family)


class AtomNode(ParseTreeNode):

    _nodeType = "ATOM"

    def terms(self):
        return [self.getValue()]

    def executeQuery(self, index):
        return index.search(self.getValue())


class PhraseNode(AtomNode):

    _nodeType = "PHRASE"

    def executeQuery(self, index):
        return index.search_phrase(self.getValue())


class GlobNode(AtomNode):

    _nodeType = "GLOB"

    def executeQuery(self, index):
        return index.search_glob(self.getValue())
