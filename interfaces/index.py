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
"""Interfaces for a text index.

$Id: index.py,v 1.1 2003/07/13 05:51:18 andyh Exp $
"""

from zope.interface import Interface


class IInjection(Interface):
    """Interface for injecting documents into an index."""

    def index_doc(docid, texts):
        """Add a document to the index.

        docid: int, identifying the document
        texts: list of unicode, the text to be indexed in a list
        return: None

        This can also be used to reindex documents.
        """

    def unindex_doc(docid):
        """Remove a document from the index.

        docid: int, identifying the document
        return: None

        If docid does not exist, KeyError is raised.
        """

class IQuerying(Interface):

    def query(querytext, start=0, count=None):
        """Execute a query.

        querytext: unicode, the query expression
        start: the first result to return (0-based)
        count: the maximum number of results to return (default: all)
        return: ([(docid, rank), ...], total)

        The return value is a triple:
            matches: list of (int, float) tuples, docid and rank
            total: int, the total number of matches

        The matches list represents the requested batch.  The ranks
        are floats between 0 and 1 (inclusive).
        """

class IStatistics(Interface):

    def documentCount():
        """Return the number of documents currently indexed."""

    def wordCount():
        """Return the number of words currently indexed."""


class IExtendedQuerying(Interface):

    def search(term):
        """Execute a search on a single term given as a string.

        Return an IIBTree mapping docid to score, or None if all docs
        match due to the lexicon returning no wids for the term (e.g.,
        if the term is entirely composed of stopwords).
        """

    def search_phrase(phrase):
        """Execute a search on a phrase given as a string.

        Return an IIBtree mapping docid to score.
        """

    def search_glob(pattern):
        """Execute a pattern search.

        The pattern represents a set of words by using * and ?.  For
        example, "foo*" represents the set of all words in the lexicon
        starting with "foo".

        Return an IIBTree mapping docid to score.
        """

    def query_weight(terms):
        """Return the weight for a set of query terms.

        'terms' is a sequence of all terms included in the query,
        although not terms with a not.  If a term appears more than
        once in a query, it should appear more than once in terms.

        Nothing is defined about what "weight" means, beyond that the
        result is an upper bound on document scores returned for the
        query.
        """

class IRangeQuerying(Interface):

    def rangesearch(minval, maxval):
        """ Execute a range search.

           Return an IISet of docids for all docs where

           minval <= value <= maxval   if minval<=maxval and 
                                       both minval and maxval are not None

           value <= maxval             if minval is not None 

           value >= minval             if maxval is not None
        """             

