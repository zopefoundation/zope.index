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
"""Unit tests for TextIndexWrapper.

$Id$
"""

import unittest

from zope.index.text.textindexwrapper import TextIndexWrapper
from zope.index.text import parsetree

class TextIndexWrapperTest(unittest.TestCase):

    def setUp(self):
        w = TextIndexWrapper()
        doc = u"the quick brown fox jumps over the lazy dog"
        w.index_doc(1000, [doc])
        doc = u"the brown fox and the yellow fox don't need the retriever"
        w.index_doc(1001, [doc])
        self.wrapper = w

    def test_clear(self):
        self.wrapper.clear()
        self.assertEqual(self.wrapper.documentCount(), 0)
        self.assertEqual(self.wrapper.wordCount(), 0)

    def testCounts(self):
        w = self.wrapper
        self.assertEqual(self.wrapper.documentCount(), 2)
        self.assertEqual(self.wrapper.wordCount(), 12)
        doc = u"foo bar"
        w.index_doc(1002, [doc])
        self.assertEqual(self.wrapper.documentCount(), 3)
        self.assertEqual(self.wrapper.wordCount(), 14)

    def testOne(self):
        matches, total = self.wrapper.query(u"quick fox", 0, 10)
        self.assertEqual(total, 1)
        [(docid, rank)] = matches # if this fails there's a problem
        self.assertEqual(docid, 1000)

    def testDefaultBatch(self):
        matches, total = self.wrapper.query(u"fox", 0)
        self.assertEqual(total, 2)
        self.assertEqual(len(matches), 2)
        matches, total = self.wrapper.query(u"fox")
        self.assertEqual(total, 2)
        self.assertEqual(len(matches), 2)
        matches, total = self.wrapper.query(u" fox", 1)
        self.assertEqual(total, 2)
        self.assertEqual(len(matches), 1)

    def testGlobbing(self):
        matches, total = self.wrapper.query("fo*")
        self.assertEqual(total, 2)
        self.assertEqual(len(matches), 2)

    def testLatin1(self):
        w = self.wrapper
        doc = u"Fran\xe7ois"
        w.index_doc(1002, [doc])
        matches, total = self.wrapper.query(doc, 0, 10)
        self.assertEqual(total, 1)
        [(docid, rank)] = matches # if this fails there's a problem
        self.assertEqual(docid, 1002)

    def testUnicode(self):
        w = self.wrapper
        # Verbose, but easy to debug
        delta  = u"\N{GREEK SMALL LETTER DELTA}"
        delta += u"\N{GREEK SMALL LETTER EPSILON}"
        delta += u"\N{GREEK SMALL LETTER LAMDA}"
        delta += u"\N{GREEK SMALL LETTER TAU}"
        delta += u"\N{GREEK SMALL LETTER ALPHA}"
        self.assert_(delta.islower())
        emdash = u"\N{EM DASH}"
        self.assert_(not emdash.isalnum())
        alpha  = u"\N{GREEK SMALL LETTER ALPHA}"
        self.assert_(alpha.islower())
        lamda  = u"\N{GREEK SMALL LETTER LAMDA}"
        lamda += u"\N{GREEK SMALL LETTER ALPHA}"
        self.assert_(lamda.islower())
        doc = delta + emdash + alpha
        w.index_doc(1002, [doc])
        for word in delta, alpha:
            matches, total = self.wrapper.query(word, 0, 10)
            self.assertEqual(total, 1)
            [(docid, rank)] = matches # if this fails there's a problem
            self.assertEqual(docid, 1002)
        self.assertRaises(parsetree.ParseError,
                          self.wrapper.query, emdash, 0, 10)
        matches, total = self.wrapper.query(lamda, 0, 10)
        self.assertEqual(total, 0)

    def testNone(self):
        matches, total = self.wrapper.query(u"dalmatian", 0, 10)
        self.assertEqual(total, 0)
        self.assertEqual(len(matches), 0)

    def testAll(self):
        matches, total = self.wrapper.query(u"brown fox", 0, 10)
        self.assertEqual(total, 2)
        self.assertEqual(len(matches), 2)
        matches.sort()
        self.assertEqual(matches[0][0], 1000)
        self.assertEqual(matches[1][0], 1001)

    def testBatching(self):
        matches1, total = self.wrapper.query(u"brown fox", 0, 1)
        self.assertEqual(total, 2)
        self.assertEqual(len(matches1), 1)
        matches2, total = self.wrapper.query(u"brown fox", 1, 1)
        self.assertEqual(total, 2)
        self.assertEqual(len(matches2), 1)
        matches = matches1 + matches2
        matches.sort()
        self.assertEqual(matches[0][0], 1000)
        self.assertEqual(matches[1][0], 1001)

def test_suite():
    return unittest.makeSuite(TextIndexWrapperTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
