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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Filters for TopicIndexes
"""

import BTrees

from zope.index.topic.interfaces import ITopicFilteredSet
from zope.interface import implementer

@implementer(ITopicFilteredSet)
class FilteredSetBase(object):
    """
    Base class for all filtered sets.

    A filtered set is a collection of documents represented by their
    document ids that match a common criteria given by a condition.
    """

    family = BTrees.family32

    def __init__(self, id, expr, family=None):
        if family is not None:
            self.family = family
        self.id = id
        self.expr = expr
        self.clear()

    def clear(self):
        self._ids = self.family.IF.Set()

    def index_doc(self, docid, context):
        raise NotImplementedError

    def unindex_doc(self, docid):
        try:
            self._ids.remove(docid)
        except KeyError:
            pass

    def getId(self):
        return self.id

    def getExpression(self):
        return self.expr

    def setExpression(self, expr):
        self.expr = expr

    def getIds(self):
        return self._ids

    def __repr__(self): # pragma: no cover
        return '%s: (%s) %s' % (self.id, self.expr, list(self._ids))

    __str__ = __repr__


class PythonFilteredSet(FilteredSetBase):
    """ a topic filtered set to check a context against a Python expression """

    def index_doc(self, docid, context):
        try:
            if eval(self.expr):
                self._ids.insert(docid)
        except:
            pass  # ignore errors
