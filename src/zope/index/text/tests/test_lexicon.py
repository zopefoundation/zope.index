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
"""Lexicon tests
"""
import unittest


class LexiconTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.index.text.lexicon import Lexicon
        return Lexicon

    def _makeOne(self, *pipeline):
        from zope.index.text.lexicon import Splitter
        pipeline = (Splitter(),) + pipeline
        return self._getTargetClass()(*pipeline)

    def test_class_conforms_to_ILexicon(self):
        from zope.interface.verify import verifyClass

        from zope.index.text.interfaces import ILexicon
        verifyClass(ILexicon, self._getTargetClass())

    def test_instance_conforms_to_ILexicon(self):
        from zope.interface.verify import verifyObject

        from zope.index.text.interfaces import ILexicon
        verifyObject(ILexicon, self._makeOne())

    def test_empty(self):
        lexicon = self._makeOne()
        self.assertEqual(len(lexicon.words()), 0)
        self.assertEqual(len(lexicon.wids()), 0)
        self.assertEqual(len(lexicon.items()), 0)
        self.assertEqual(lexicon.wordCount(), 0)

    def test_wordCount_legacy_instance_no_write_on_read(self):
        from BTrees.Length import Length
        lexicon = self._makeOne()
        # Simulate old instance, which didn't have Length attr
        del lexicon.wordCount
        self.assertEqual(lexicon.wordCount(), 0)
        # No write-on-read!
        self.assertNotIsInstance(lexicon.wordCount, Length)

    def test_sourceToWordIds_empty_string(self):
        lexicon = self._makeOne()
        wids = lexicon.sourceToWordIds('')
        self.assertEqual(wids, [])

    def test_sourceToWordIds_none(self):
        # See LP #598776
        lexicon = self._makeOne()
        wids = lexicon.sourceToWordIds(None)
        self.assertEqual(wids, [])

    def test_sourceToWordIds(self):
        lexicon = self._makeOne()
        wids = lexicon.sourceToWordIds('cats and dogs')
        self.assertEqual(wids, [1, 2, 3])
        self.assertEqual(lexicon.get_word(1), 'cats')
        self.assertEqual(lexicon.get_wid('cats'), 1)

    def test_sourceToWordIds_promotes_wordCount_attr(self):
        from BTrees.Length import Length
        lexicon = self._makeOne()
        # Simulate old instance, which didn't have Length attr
        del lexicon.wordCount
        wids = lexicon.sourceToWordIds('cats and dogs')
        self.assertEqual(wids, [1, 2, 3])
        self.assertEqual(lexicon.wordCount(), 3)
        self.assertIsInstance(lexicon.wordCount, Length)

    def test_termToWordIds_hit(self):
        lexicon = self._makeOne()
        lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('dogs')
        self.assertEqual(wids, [3])

    def test_termToWordIds_miss(self):
        lexicon = self._makeOne()
        lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('boxes')
        self.assertEqual(wids, [0])

    def test_termToWordIds_w_extra_pipeline_element(self):
        lexicon = self._makeOne(StupidPipelineElement('dogs', 'fish'))
        lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('fish')
        self.assertEqual(wids, [3])

    def test_termToWordIds_w_case_normalizer(self):
        from zope.index.text.lexicon import CaseNormalizer
        lexicon = self._makeOne(CaseNormalizer())
        lexicon.sourceToWordIds('CATS and dogs')
        wids = lexicon.termToWordIds('cats and dogs')
        self.assertEqual(wids, [1, 2, 3])

    def test_termToWordIds_wo_case_normalizer(self):
        lexicon = self._makeOne()
        wids = lexicon.sourceToWordIds('CATS and dogs')
        wids = lexicon.termToWordIds('cats and dogs')
        self.assertEqual(wids, [0, 2, 3])

    def test_termToWordIds_w_two_extra_pipeline_elements(self):
        lexicon = self._makeOne(StupidPipelineElement('cats', 'fish'),
                                WackyReversePipelineElement('fish'),
                                )
        lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('hsif')
        self.assertEqual(wids, [1])

    def test_termToWordIds_w_three_extra_pipeline_elements(self):
        lexicon = self._makeOne(StopWordPipelineElement({'and': 1}),
                                StupidPipelineElement('dogs', 'fish'),
                                WackyReversePipelineElement('fish'),
                                )
        wids = lexicon.sourceToWordIds('cats and dogs')
        wids = lexicon.termToWordIds('hsif')
        self.assertEqual(wids, [2])

    def test_parseTerms_tuple(self):
        TERMS = ('a', 'b*c', 'de?f')
        lexicon = self._makeOne()
        self.assertEqual(lexicon.parseTerms(TERMS), list(TERMS))

    def test_parseTerms_list(self):
        TERMS = ('a', 'b*c', 'de?f')
        lexicon = self._makeOne()
        self.assertEqual(lexicon.parseTerms(TERMS), list(TERMS))

    def test_parseTerms_empty_string(self):
        lexicon = self._makeOne()
        self.assertEqual(lexicon.parseTerms('a b*c de?f'),
                         ['a', 'b*c', 'de?f'])

    def test_parseTerms_nonempty_string(self):
        lexicon = self._makeOne()
        self.assertEqual(lexicon.parseTerms(''), [])

    def test_isGlob_empty(self):
        lexicon = self._makeOne()
        self.assertFalse(lexicon.isGlob(''))

    def test_isGlob_miss(self):
        lexicon = self._makeOne()
        self.assertFalse(lexicon.isGlob('abc'))

    def test_isGlob_question_mark(self):
        lexicon = self._makeOne()
        self.assertTrue(lexicon.isGlob('a?c'))

    def test_isGlob_asterisk(self):
        lexicon = self._makeOne()
        self.assertTrue(lexicon.isGlob('abc*'))

    def test_globToWordIds_invalid_pattern(self):
        from zope.index.text.parsetree import QueryError
        lexicon = self._makeOne()
        lexicon.sourceToWordIds('cats and dogs')
        self.assertRaises(QueryError, lexicon.globToWordIds, '*s')

    def test_globToWordIds_simple_pattern(self):
        lexicon = self._makeOne()
        lexicon.sourceToWordIds('cats and dogs are enemies')
        self.assertEqual(lexicon.globToWordIds('a*'), [2, 4])

    def test_globToWordIds_simple_pattern2(self):
        lexicon = self._makeOne()
        lexicon.sourceToWordIds('cats and dogs are enemies')
        self.assertEqual(lexicon.globToWordIds('a?e'), [4])

    def test_globToWordIds_prefix(self):
        lexicon = self._makeOne()
        lexicon.sourceToWordIds('cats and dogs are enemies')
        self.assertEqual(lexicon.globToWordIds('are'), [4])

    def test_getWordIdCreate_new(self):
        lexicon = self._makeOne()
        wid = lexicon._getWordIdCreate('nonesuch')
        self.assertEqual(wid, 1)
        self.assertEqual(lexicon.get_word(1), 'nonesuch')
        self.assertEqual(lexicon.get_wid('nonesuch'), 1)

    def test_getWordIdCreate_extant(self):
        lexicon = self._makeOne()
        lexicon.sourceToWordIds('cats and dogs are enemies')
        wid = lexicon._getWordIdCreate('cats')
        self.assertEqual(wid, 1)
        self.assertEqual(lexicon.get_word(1), 'cats')
        self.assertEqual(lexicon.get_wid('cats'), 1)

    def test__new_wid_recovers_from_damaged_length(self):
        lexicon = self._makeOne()
        lexicon.sourceToWordIds('cats and dogs')
        lexicon.wordCount.set(0)
        wid = lexicon._new_wid()
        self.assertEqual(wid, 4)
        self.assertEqual(lexicon.wordCount(), 4)


class SplitterTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.index.text.lexicon import Splitter
        return Splitter

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_ISplitter(self):
        from zope.interface.verify import verifyClass

        from zope.index.text.interfaces import ISplitter
        verifyClass(ISplitter, self._getTargetClass())

    def test_instance_conforms_to_ISplitter(self):
        from zope.interface.verify import verifyObject

        from zope.index.text.interfaces import ISplitter
        verifyObject(ISplitter, self._makeOne())

    def test_process_empty_string(self):
        splitter = self._makeOne()
        self.assertEqual(splitter.process(['']), [])

    def test_process_simple(self):
        splitter = self._makeOne()
        self.assertEqual(splitter.process(['abc def']), ['abc', 'def'])

    def test_process_w_locale_awareness(self):
        import locale
        import sys
        old_locale = locale.setlocale(locale.LC_ALL)
        # set German locale
        try:
            locale_string = (
                'German_Germany.1252' if sys.platform == 'win32'
                else 'de_DE.ISO8859-1')
            locale.setlocale(locale.LC_ALL, locale_string)
        except locale.Error:  # pragma: no cover
            self.skipTest("de._DE.ISO8859-1 locale is not available")
        self.addCleanup(locale.setlocale, locale.LC_ALL, old_locale)

        expected = ['m\xfclltonne', 'waschb\xe4r',
                    'beh\xf6rde', '\xfcberflieger']
        splitter = self._makeOne()
        self.assertEqual(splitter.process([' '.join(expected)]), expected)

    def test_process_w_glob(self):
        splitter = self._makeOne()
        self.assertEqual(splitter.process(['abc?def hij*klm nop* qrs?']),
                         ['abc', 'def', 'hij', 'klm', 'nop', 'qrs'])

    def test_processGlob_empty_string(self):
        splitter = self._makeOne()
        self.assertEqual(splitter.processGlob(['']), [])

    def test_processGlob_simple(self):
        splitter = self._makeOne()
        self.assertEqual(splitter.processGlob(['abc def']), ['abc', 'def'])

    def test_processGlob_w_glob(self):
        splitter = self._makeOne()
        self.assertEqual(splitter.processGlob(['abc?def hij*klm nop* qrs?']),
                         ['abc?def', 'hij*klm', 'nop*', 'qrs?'])


class CaseNormalizerTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.index.text.lexicon import CaseNormalizer
        return CaseNormalizer

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IPipelineElement(self):
        from zope.interface.verify import verifyClass

        from zope.index.text.interfaces import IPipelineElement
        verifyClass(IPipelineElement, self._getTargetClass())

    def test_instance_conforms_to_IPipelineElement(self):
        from zope.interface.verify import verifyObject

        from zope.index.text.interfaces import IPipelineElement
        verifyObject(IPipelineElement, self._makeOne())

    def test_process_empty(self):
        cn = self._makeOne()
        self.assertEqual(cn.process([]), [])

    def test_process_nonempty(self):
        cn = self._makeOne()
        self.assertEqual(cn.process(['ABC Def']), ['abc def'])


class StopWordRemoverTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.index.text.lexicon import StopWordRemover
        return StopWordRemover

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IPipelineElement(self):
        from zope.interface.verify import verifyClass

        from zope.index.text.interfaces import IPipelineElement
        verifyClass(IPipelineElement, self._getTargetClass())

    def test_instance_conforms_to_IPipelineElement(self):
        from zope.interface.verify import verifyObject

        from zope.index.text.interfaces import IPipelineElement
        verifyObject(IPipelineElement, self._makeOne())

    def test_process_empty(self):
        cn = self._makeOne()
        self.assertEqual(cn.process([]), [])

    def test_process_nonempty(self):
        QUOTE = 'The end of government is justice'
        cn = self._makeOne()
        self.assertEqual(cn.process(QUOTE.lower().split()),
                         ['end', 'government', 'justice'])


class StopWordAndSingleCharRemoverTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.index.text.lexicon import StopWordAndSingleCharRemover
        return StopWordAndSingleCharRemover

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IPipelineElement(self):
        from zope.interface.verify import verifyClass

        from zope.index.text.interfaces import IPipelineElement
        verifyClass(IPipelineElement, self._getTargetClass())

    def test_instance_conforms_to_IPipelineElement(self):
        from zope.interface.verify import verifyObject

        from zope.index.text.interfaces import IPipelineElement
        verifyObject(IPipelineElement, self._makeOne())

    def test_process_empty(self):
        cn = self._makeOne()
        self.assertEqual(cn.process([]), [])

    def test_process_nonempty(self):
        QUOTE = 'The end of government is justice z x q'
        cn = self._makeOne()
        self.assertEqual(cn.process(QUOTE.lower().split()),
                         ['end', 'government', 'justice'])


class StupidPipelineElement:
    def __init__(self, fromword, toword):
        self.__fromword = fromword
        self.__toword = toword

    def process(self, seq):
        res = []
        for term in seq:
            if term == self.__fromword:
                res.append(self.__toword)
            else:
                res.append(term)
        return res


class WackyReversePipelineElement:
    def __init__(self, revword):
        self.__revword = revword

    def process(self, seq):
        res = []
        for term in seq:
            if term == self.__revword:
                x = list(term)
                x.reverse()
                res.append(''.join(x))
            else:
                res.append(term)
        return res


class StopWordPipelineElement:

    def __init__(self, stopdict):
        self.__stopdict = stopdict

    def process(self, seq):
        res = []
        for term in seq:
            if self.__stopdict.get(term):
                continue
            else:
                res.append(term)
        return res
