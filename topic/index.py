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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Topic index

$Id$
"""
from persistent import Persistent

from BTrees.OOBTree import OOBTree
from BTrees.IIBTree import IISet, union, intersection

from types import ListType, TupleType, StringTypes
from zope.interface import implements

from zope.index.interfaces import IInjection
from zope.index.topic.interfaces import ITopicQuerying

class TopicIndex(Persistent):

    implements(IInjection, ITopicQuerying)

    def __init__(self):
        self.clear()

    def clear(self):
        # mapping filter id -> filter
        self._filters = OOBTree()

    def addFilter(self, f ):
        """ Add filter 'f' with ID 'id' """
        self._filters[f.getId()] = f

    def delFilter(self, id):
        """ remove a filter given by its ID 'id' """
        del self._filters[id]

    def index_doc(self, docid, obj):
        """index an object"""

        for f in self._filters.values():
            f.index_doc(docid, obj)

    def unindex_doc(self, docid):
        """unindex an object"""

        for f in self._filters.values():
            f.unindex_doc(docid)

    def search(self, query, operator='and'):

        if isinstance(query, StringTypes): query = [query]
        if not isinstance(query, (TupleType, ListType)):
            raise TypeError, 'query argument must be a list/tuple of filter ids'

        f = {'and' : intersection, 'or' : union}[operator]
    
        rs = None
        for id in self._filters.keys():
            if id in query:
                docids = self._filters[id].getIds()
                rs = f(rs, docids)
            
        if rs:  return rs
        else: return IISet()
        
