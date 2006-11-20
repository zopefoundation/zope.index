Field Indexes
=============

Field indexes index orderable values.  Note that they don't check for
orderability. That is, all of the values added to the index must be
orderable together. It is up to applications to provide only mutually
orderable values.

    >>> from zope.index.field import FieldIndex

    >>> index = FieldIndex()
    >>> index.index_doc(0, 6)
    >>> index.index_doc(1, 26)
    >>> index.index_doc(2, 94)
    >>> index.index_doc(3, 68)
    >>> index.index_doc(4, 30)
    >>> index.index_doc(5, 68)
    >>> index.index_doc(6, 82)
    >>> index.index_doc(7, 30)
    >>> index.index_doc(8, 43)
    >>> index.index_doc(9, 15)

Fied indexes are searched with apply.  The argument is a tuple
with a minimum and maximum value:

    >>> index.apply((30, 70))
    IFSet([3, 4, 5, 7, 8])

A common mistake is to pass a single value.  If anything other than a 
tw-tuple is passed, a type error is raised:

    >>> index.apply('hi')
    Traceback (most recent call last):
    ...
    TypeError: ('two-length tuple expected', 'hi')


Open-ended ranges can be provided by provinding None as an end point:

    >>> index.apply((30, None))
    IFSet([2, 3, 4, 5, 6, 7, 8])

    >>> index.apply((None, 70))
    IFSet([0, 1, 3, 4, 5, 7, 8, 9])

    >>> index.apply((None, None))
    IFSet([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

To do an exact value search, supply equal minimum and maximum values:

    >>> index.apply((30, 30))
    IFSet([4, 7])

    >>> index.apply((70, 70))
    IFSet([])

Field indexes support basic statistics:

    >>> index.documentCount()
    10
    >>> index.wordCount()
    8

Documents can be reindexed:

    >>> index.apply((15, 15))
    IFSet([9])
    >>> index.index_doc(9, 14)

    >>> index.apply((15, 15))
    IFSet([])
    >>> index.apply((14, 14))
    IFSet([9])
    
Documents can be unindexed:

    >>> index.unindex_doc(7)
    >>> index.documentCount()
    9
    >>> index.wordCount()
    8
    >>> index.unindex_doc(8)
    >>> index.documentCount()
    8
    >>> index.wordCount()
    7

    >>> index.apply((30, 70))
    IFSet([3, 4, 5])

Unindexing a document id that isn't present is ignored:

    >>> index.unindex_doc(8)
    >>> index.unindex_doc(80)
    >>> index.documentCount()
    8
    >>> index.wordCount()
    7

We can also clear the index entirely:

    >>> index.clear()
    >>> index.documentCount()
    0
    >>> index.wordCount()
    0

    >>> index.apply((30, 70))
    IFSet([])

Bugfix testing:
---------------
Happened at least once that the value dropped out of the forward index,
but the index still contains the object, the unindex broke

    >>> index.index_doc(0, 6)
    >>> index.index_doc(1, 26)
    >>> index.index_doc(2, 94)
    >>> index.index_doc(3, 68)
    >>> index.index_doc(4, 30)
    >>> index.index_doc(5, 68)
    >>> index.index_doc(6, 82)
    >>> index.index_doc(7, 30)
    >>> index.index_doc(8, 43)
    >>> index.index_doc(9, 15)
    
    >>> index.apply((None, None))
    IFSet([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

Here is the damage:

    >>> del index._fwd_index[68]
    
Unindex should succeed:
    
    >>> index.unindex_doc(5)
    >>> index.unindex_doc(3)
    
    >>> index.apply((None, None))
    IFSet([0, 1, 2, 4, 6, 7, 8, 9])

Bugfix testing:
---------------
Happened at least once that the value dropped out of the forward index,
but the index still contains the object, the unindex broke

    >>> index.index_doc(0, 6)
    >>> index.index_doc(1, 26)
    >>> index.index_doc(2, 94)
    >>> index.index_doc(3, 68)
    >>> index.index_doc(4, 30)
    >>> index.index_doc(5, 68)
    >>> index.index_doc(6, 82)
    >>> index.index_doc(7, 30)
    >>> index.index_doc(8, 43)
    >>> index.index_doc(9, 15)
    
    >>> index.apply((None, None))
    IFSet([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

Here is the damage:

    >>> del index._fwd_index[68]
    
Unindex should succeed:
    
    >>> index.unindex_doc(5)
    >>> index.unindex_doc(3)
    
    >>> index.apply((None, None))
    IFSet([0, 1, 2, 4, 6, 7, 8, 9])
