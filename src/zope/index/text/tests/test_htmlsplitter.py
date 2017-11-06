##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Test zope.index.text.htmlsplitter
"""

from zope.index.text.tests.test_lexicon import SplitterTests

class HTMLWordSplitterTests(SplitterTests):

    def _getTargetClass(self):
        from zope.index.text.htmlsplitter import HTMLWordSplitter
        return HTMLWordSplitter

    def _makeOne(self):
        return self._getTargetClass()()

    def test_process_w_markup(self):
        splitter = self._makeOne()
        self.assertEqual(splitter.process(['<h1>abc</h1> &nbsp; <p>def</p>']),
                         ['abc', 'def'])

    def test_process_w_markup_no_spaces(self):
        splitter = self._makeOne()
        self.assertEqual(splitter.process(['<h1>abc</h1>&nbsp;<p>def</p>']),
                         ['abc', 'def'])

    def test_processGlob_w_markup_no_glob(self):
        splitter = self._makeOne()
        self.assertEqual(splitter.processGlob(['<h1>abc</h1> &nbsp; '
                                               '<p>def</p>']),
                         ['abc', 'def'])
