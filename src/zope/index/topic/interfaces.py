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
"""Basic interfaces shared between different types of index.
"""
from zope.interface import Interface


class ITopicQuerying(Interface):
    """Query over topics, seperated by white space."""

    def search(query, operator='and'):
        """
        Execute a search given by *query* as a list/tuple of filter ids.

        *operator* can be ``'and'`` or ``'or'`` to search for matches in all
        or any filter.

        Return an IFSet of docids
        """


class ITopicFilteredSet(Interface):
    """Interface for filtered sets used by topic indexes."""

    def clear():
        """Remove all entries from the index."""

    def index_doc(docid, context):
        """Add an object's info to the index."""

    def unindex_doc(docid):
        """Remove an object with id 'docid' from the index."""

    def getId():
        """Return the id of the filter itself."""

    def setExpression(expr):
        """Set the filter expression, e.g. 'context.meta_type=='...'"""

    def getExpression():
        """Return the filter expression."""

    def getIds():
        """Return an IFSet of docids."""
