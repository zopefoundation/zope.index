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
"""Basic interfaces shared between different types of index.

$Id$
"""
from zope.interface import Interface


class IInjection(Interface):
    """Interface for injecting documents into an index."""

    def index_doc(docid, doc):
        """Add a document to the index.

        docid: int, identifying the document
        doc: the document to be indexed
        return: None

        This can also be used to reindex documents.
        """

    def unindex_doc(docid):
        """Remove a document from the index.

        docid: int, identifying the document
        return: None

        This call is a no-op if the docid isn't in the index, however,
        after this call, the index should have no references to the docid.
        """

    def clear():
        """Unindex all documents indexed by the index
        """

class IQuerying(Interface):
    """An index that can be queried by some text and returns a result set."""

    def query(querytext, start=0, count=None):
        """Execute a query.

        querytext: unicode, the query expression
        start: the first result to return (0-based)
        count: the maximum number of results to return (default: all)
        return: ([(docid, rank), ...], total)

        The return value is a tuple:
            matches: list of (int, float) tuples, docid and rank
            total: int, the total number of matches

        The matches list represents the requested batch.  The ranks
        are floats between 0 and 1 (inclusive).
        """

class IStatistics(Interface):
    """An index that provides statistical information about itself."""

    def documentCount():
        """Return the number of documents currently indexed."""

    def wordCount():
        """Return the number of words currently indexed."""


class IExtendedQuerying(Interface):
    """An index that supports advanced search setups."""

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
    """Query over a range of objects."""

    def rangesearch(minval, maxval):
        """Execute a range search.

           Return an IISet of docids for all docs where

           minval <= value <= maxval   if minval<=maxval and 
                                       both minval and maxval are not None

           Value <= maxval             if minval is not None 

           value >= minval             if maxval is not None
        """             

class IKeywordQuerying(Interface):
    """Query over a set of keywords, seperated by white space."""

    def search(query, operator='and'):
        """Execute a search given by 'query' as a list/tuple of
           (unicode) strings against the index. 'operator' can be either
           'and' or 'or' to search for all keywords or any keyword. 

           Return an IISet of docids
        """

class ITopicQuerying(Interface):
    """Query over topics, seperated by white space."""

    def search(query, operator='and'):
        """Execute a search given by 'query' as a list/tuple of filter ids.
          'operator' can be 'and' or 'or' to search for matches in all
           or any filter.

           Return an IISet of docids
        """

class ISimpleQuery(Interface):
    """A simple query interface."""

    def query(term, start=0, count=None):
        """Search for the given term, return a sequence of docids"""


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
        """Return an IISet of docids."""
