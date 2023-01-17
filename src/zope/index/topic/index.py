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
"""Topic index
"""
import BTrees
from persistent import Persistent
from zope.interface import implementer

from zope.index.interfaces import IIndexSearch
from zope.index.interfaces import IInjection
from zope.index.topic.interfaces import ITopicQuerying


@implementer(IInjection, ITopicQuerying, IIndexSearch)
class TopicIndex(Persistent):
    """
    Topic index.

    Implements :class:`zope.index.interfaces.IInjection`,
    :class:`zope.index.interfaces.IIndexSearch` and
    :class:`zope.index.topic.interfaces.ITopicQuerying`.
    """

    family = BTrees.family32

    def __init__(self, family=None):
        if family is not None:
            self.family = family
        self.clear()

    def clear(self):
        # mapping filter id -> filter
        self._filters = self.family.OO.BTree()

    def addFilter(self, f):
        """ Add filter 'f' with ID 'id' """
        self._filters[f.getId()] = f

    def delFilter(self, id):
        """ remove a filter given by its ID 'id' """
        del self._filters[id]

    def clearFilters(self):
        """ Clear existing filters of their docids, but leave them in place.
        """
        for filter in self._filters.values():
            filter.clear()

    def index_doc(self, docid, obj):
        """index an object"""

        for f in self._filters.values():
            f.index_doc(docid, obj)

    def unindex_doc(self, docid):
        """unindex an object"""

        for f in self._filters.values():
            f.unindex_doc(docid)

    def search(self, query, operator='and'):
        if isinstance(query, str):
            query = [query]

        if not isinstance(query, (tuple, list)):
            raise TypeError(
                'query argument must be a list/tuple of filter ids')

        sets = []
        for id in self._filters.keys():
            if id in query:
                docids = self._filters[id].getIds()
                sets.append(docids)

        if operator == 'or':
            rs = self.family.IF.multiunion(sets)
        elif operator == 'and':
            # sort smallest to largest set so we intersect the smallest
            # number of document identifiers possible
            sets.sort(key=len)
            rs = None
            for set in sets:
                rs = self.family.IF.intersection(rs, set)
                if not rs:
                    break
        else:
            raise TypeError('Topic index only supports `and` and `or` '
                            'operators, not `%s`.' % operator)

        if rs:
            return rs
        else:
            return self.family.IF.Set()

    def apply(self, query):
        operator = 'and'
        if isinstance(query, dict):
            if 'operator' in query:
                operator = query.pop('operator')
            query = query['query']
        return self.search(query, operator=operator)
