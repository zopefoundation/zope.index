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
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Filters for TopicIndexes"""

from zodb.btrees.IIBTree import IISet
from zope.index.interfaces import ITopicFilter
from zope.interface import implements

class FilterBase:
    """ base class for all filters """

    implements(ITopicFilter)

    def __init__(self, id, expr):
        self.id   = id
        self.expr = expr
        self.clear()

    def clear(self):
        self._ids  = IISet()

    def index_doc(self, docid, context):
        raise NotImplementedError

    def unindex_doc(self, docid):
        try: self._ids.remove(docid)
        except KeyError: pass

    def getId(self):            
        return self.id

    def getExpression(self):    
        return self.expr

    def setExpression(self, expr): 
        self.expr = expr

    def getIds(self): 
        return self._ids

    def __repr__(self):
        return '%s: (%s) %s' % (self.id, self.expr, map(None, self._ids))

    __str__ = __repr__


class PythonFilter(FilterBase):
    """ a topic filter to check a context against a Python expression """

    def index_doc(self, docid, context):

        try:
            if eval(self.expr): self._ids.insert(docid)
        except:
            pass  # ignore errors 


