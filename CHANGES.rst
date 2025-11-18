Change log
==========

8.1 (2025-11-18)
----------------

- Move all supported package metadata into ``pyproject.toml``.

- Drop support for Python 3.9.

- Add support for Python 3.14.


8.0 (2025-09-12)
----------------

- Replace ``pkg_resources`` namespace with PEP 420 native namespace.

- Drop support for Python 3.8.

- Add preliminary support for Python 3.14.


7.0 (2024-09-18)
----------------

- Add final support for Python 3.13.

- Drop support for Python 3.7.

- C extension now enables multi-phase module initialization (PEP 489).See:
  https://docs.python.org/3.13/howto/isolating-extensions.html

- Build Windows wheels on GHA.


6.1 (2024-02-02)
----------------

- Add support for Python 3.12.

- Add preliminary support for Python 3.13 as of 3.13a3.

- Fix error in ``OkapiIndex._search_wids`` for Python 3.10+, occurring when a
  word is contained in more than 10 documents.
  `#48 <https://github.com/zopefoundation/zope.index/pull/48>`_


6.0 (2023-03-24)
----------------

- Add support for Python 3.11.

- Add preliminary support for Python 3.12a5.

- Drop support for Python 2.7, 3.5, 3.6.


5.2.1 (2022-09-15)
------------------

- Disable unsafe math optimizations in C code.  See `pull request 40
  <https://github.com/zopefoundation/zope.index/pull/40>`_.


5.2.0 (2022-04-06)
------------------

- Add support for Python 3.10.


5.1.0 (2021-07-19)
------------------

- Add support for Python 3.9.

- Build aarch64 wheels.


5.0.0 (2019-11-12)
------------------

- Fix ``zope.index.text.ricecode.decode_deltas(..., [])``.  See
  `issue 22 <https://github.com/zopefoundation/zope.index/issues/22>`_.

- Drop support for Python 3.4.

- Add support for Python 3.8.


4.4.0 (2018-10-05)
------------------

- Drop support for Python 3.3.

- Add support for Python 3.7. ``SortingIndexMixin.sort`` now just
  returns instead of raising ``StopIteration`` as required by
  :pep:`479`. See `issue 20 <https://github.com/zopefoundation/zope.index/pull/20>`_.

- Docs are now hosted at https://zopeindex.readthedocs.io/

- Drop support for ``setup.py test``.

- Remove some internal test scripts that were never ported to Python 3.

- Reach and maintain 100% test coverage.


4.3.0 (2017-04-24)
------------------

- ``None`` are now valid values in a field index. This requires BTrees
  >= 4.4.1.
- Allow ``TypeError`` to propagate from a field index when the value
  cannot be stored in a BTree. Previously it was silently ignored
  because it was expected that these were usually ``None``.
- Add support for Python 3.6. See `issue 8
  <https://github.com/zopefoundation/zope.index/issues/8>`_.
- Make the C implementation of the text index's score function
  (``zope.text.index.okascore``) importable under Python 3. Previously
  we would fall back to a pure-Python implementation. See `issue 14
  <https://github.com/zopefoundation/zope.index/issues/14>`_.
- Packaging: Distribute ``manylinux`` wheels and Windows wheels.


4.2.0 (2016-06-10)
------------------

- Drop support for Python 2.6.

- Add support for Python 3.5.


4.1.0 (2014-12-27)
------------------

- Add support for PyPy.  (PyPy3 is pending release of a fix for:
  https://bitbucket.org/pypy/pypy/issue/1946)

- Add support for Python 3.4.

- Add support for testing on Travis.


4.0.1 (2013-02-28)
------------------

- Add the forgotten dependency on ``six``.
  Fixes https://github.com/zopefoundation/zope.index/issues/1.


4.0.0 (2013-02-25)
------------------

- Add support for Python 3.3.

- Replace deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Drop support for Python 2.4 and 2.5.


3.6.4 (2012-03-12)
------------------

- Insure proper unindex behavior if index_doc is called with a empty sequence.

- Use the standard Python doctest module instead of zope.testing.doctest


3.6.3 (2011-12-03)
------------------

- KeywordIndex: Minor optimization; use __nonzero__ instead of __len__
  to avoid loading the full TreeSet.


3.6.2 (2011-12-03)
------------------

- KeywordIndex: Store docids in TreeSet rather than a Set when the
  number of documents matching a word reaches a configurable
  threshold (default 64). The rule is applied to individual words at
  indexing time, but you can call the new optimize method to optimize
  all the words in an index at once. Designed to fix LP #881950.


3.6.1 (2010-07-08)
------------------

- TextIndex:  reuse the lexicon from the underlying Okapi / Cosine
  index, if passed.  (LP #232516)

- Lexicon:  avoid raising an exception when indexing None. (LP #598776)


3.6.0 (2009-08-03)
------------------

- Improve test readability and reached 100% test coverage.

- Fix a broken optimization in okascore.c: it was passing a Python
  float to the PyInt_AS_LONG() macro. This resulted in wrong scores,
  especially on 64 bit platforms, where all scores typically ended up
  being zero.

- Change okascore.c to produce the same results as its Python
  equivalent, reducing the brittleness of the text index tests.


3.5.2 (2009-06-09)
------------------

- Port okascore.c optimization used in okapiiindex from Zope2 catalog
  implementation.  This module is compiled conditionally, based on
  whether your environment has a working C compiler.

- Don't use ``len(self._docweight)`` in okapiindex _search_wids method
  (obtaining the length of a BTree is very expensive at scale).
  Instead use self.documentCount().  Also a Zope2 port.


3.5.1 (2009-02-27)
------------------

- The baseindex, okapiindex, and lexicon used plain counters for various
  lengths, which is unsuitable for production applications.
  Backport code from Zope2 indexes which opportunistically replaces the
  counters with BTree.Length objects.

- Backport non-insane version of baseindex._del_wordinfo from
  Zope2 text index.  This improves deletion performance by
  several orders of magnitude.

- Don't modify given query dictionary in the KeywordIndex.apply method.

- Move FieldIndex's sorting functionality to a mixin class so it can
  be reused by zc.catalog's ValueIndex.


3.5.0 (2008-12-30)
------------------

- Remove zope.testing from dependencies, as it's not really needed.

- Define IIndexSort interface for indexes that support sorting.

- Implement sorting for FieldIndex (adapted from repoze.catalog/ZCatalog).

- Add an ``apply`` method for KeywordIndex/TopicIndex, making them
  implement IIndexSearch that can be useful in catalog.

- Optimize the ``search`` method of KeywordIndex/TopicIndex by using
  multiunion for the ``or`` operator and sorting before intersection for ``and``.

- IMPORTANT: KeywordIndex/TopicIndex now use IFSets instead of IISets.
  This makes it more compatible with other indexes (for example, when
  using in catalog). This change can lead to problems, if your code somehow
  depends on the II nature of sets, as it was before.

  Also, FilteredSets used to use IFSets as well, if you have any
  FilteredSets pickled in the database, you need to migrate them to
  IFSets yourself. You can do it like that:

      filter._ids = filter.family.IF.Set(filter._ids)

  Where ``filter`` is an instance of FilteredSet.

- IMPORTANT: KeywordIndex are now non-normalizing. Because
  it can be useful for non-string keywords, where case-normalizing
  doesn't make any sense. Instead, it provides the ``normalize``
  method that can be overriden by subclasses to provide some
  normalization.

  The CaseInsensitiveKeywordIndex class is now provided that
  do case-normalization for string-based keywords. The old
  CaseSensitiveKeywordIndex is gone, applications should use
  KeywordIndex for that.

Looks like the KeywordIndex/TopicIndex was sort of abadonware
and wasn't used by application developers, so after some
discussion we decided to refactor them to make them more
usable, optimal and compatible with other indexes and catalog.

Porting application from old KeywordIndex/TopicIndex to new
ones are rather easy and explained above, so we believe that
it isn't a problem. Please, use zope3-users@zope.org or
zope-dev@zope.org mailing lists, if you have any problems
with migration.

Thanks Chris McDonough of repoze for supporting and useful code.


3.4.1 (2007-09-28)
------------------

- Fix bug in package metadata (wrong homepage URL).


3.4.0 (2007-09-28)
------------------

No further changes since 3.4.0a1.


3.4.0a1 (2007-04-22)
--------------------

Initial release as a separate project, corresponds to zope.index from
Zope 3.4.0a1
