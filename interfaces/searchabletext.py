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
"""Interfaces related to text indexing and searching.

$Id: interfaces.py 25353 2004-06-11 15:22:11Z gintautasm $
"""
from zope.interface import Interface

class ISearchableText(Interface):
    """Interface that text-indexable objects should implement."""

    def getSearchableText():
        """Return a sequence of unicode strings to be indexed.

        Each unicode string in the returned sequence will be run
        through the splitter pipeline; the combined stream of words
        coming out of the pipeline will be indexed.

        returning None indicates the object should not be indexed
        """
