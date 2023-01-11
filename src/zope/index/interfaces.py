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


class IInjection(Interface):
    """Interface for injecting documents into an index."""

    def index_doc(docid, value):
        """Add a document to the index.

        docid: int, identifying the document

        value: the value to be indexed

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


class IIndexSearch(Interface):
    """
    Interface for searching indexes.
    """

    def apply(query):
        """Apply an index to the given query

        The type of the query is index specific.

        TODO
            This is somewhat problemetic. It means that application
            code that calls apply has to be aware of the
            expected query type. This isn't too much of a problem now,
            as we have no more general query language nor do we have
            any sort of automatic query-form generation.

            It would be nice to have a system later for having
            query-form generation or, perhaps, some sort of query
            language. At that point, we'll need some sort of way to
            determine query types, presumably through introspection of
            the index objects.

        A result is returned that is:

        - An IFBTree or an IFBucket mapping document ids to floating-point
          scores for document ids of documents that match the query,

        - An IFSet or IFTreeSet containing document ids of documents
          that match the query, or

        - None, indicating that the index could not use the query and
          that the result should have no impact on determining a final
          result.

        """


class IIndexSort(Interface):
    """
    Interface for sorting documents.
    """

    def sort(docids, reverse=False, limit=None):
        """Sort document ids sequence using indexed values

        If some of docids are not indexed they are skipped
        from resulting iterable.

        Return a sorted iterable of document ids. Limited by
        value of the "limit" argument and optionally
        reversed, using the "reverse" argument.
        """


class IStatistics(Interface):
    """An index that provides statistical information about itself."""

    def documentCount():
        """Return the number of documents currently indexed."""

    def wordCount():
        """Return the number of words currently indexed."""


class INBest(Interface):
    """Interface for an N-Best chooser."""

    def add(item, score):
        """Record that item 'item' has score 'score'.  No return value.

        The N best-scoring items are remembered, where N was passed to
        the constructor.  'item' can by anything.  'score' should be
        a number, and larger numbers are considered better.
        """

    def addmany(sequence):
        """Like "for item, score in sequence: self.add(item, score)".

        This is simply faster than calling add() len(seq) times.
        """

    def getbest():
        """Return the (at most) N best-scoring items as a sequence.

        The return value is a sequence of 2-tuples, (item, score), with
        the largest score first.  If .add() has been called fewer than
        N times, this sequence will contain fewer than N pairs.
        """

    def pop_smallest():
        """Return and remove the (item, score) pair with lowest score.

        If len(self) is 0, raise IndexError.

        To be cleaer, this is the lowest score among the N best-scoring
        seen so far.  This is most useful if the capacity of the NBest
        object is never exceeded, in which case  pop_smallest() allows
        using the object as an ordinary smallest-in-first-out priority
        queue.
        """

    def __len__():
        """Return the number of (item, score) pairs currently known.

        This is N (the value passed to the constructor), unless .add()
        has been called fewer than N times.
        """

    def capacity():
        """Return the maximum number of (item, score) pairs.

        This is N (the value passed to the constructor).
        """
