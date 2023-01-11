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
"""HTML Splitter
"""
import re

from zope.interface import implementer

from zope.index.text.interfaces import ISplitter


MARKUP = re.compile(r"(<[^<>]*>|&[A-Za-z]+;)")

_flags = 0
WORDS = re.compile(r"\w+", _flags)
GLOBS = re.compile(r"\w+[\w*?]*", _flags)
del _flags


@implementer(ISplitter)
class HTMLWordSplitter:
    """
    Implementation of :class:`zope.index.text.interfaces.ISplitter`
    that removes HTML tags.
    """

    def process(self, text):
        return self._apply(text, WORDS)

    def processGlob(self, text):
        # see Lexicon.globToWordIds()
        return self._apply(text, GLOBS)

    def _apply(self, text, pattern):
        result = []
        for chunk in text:
            result.extend(self._split(chunk, pattern))
        return result

    def _split(self, text, pattern):
        text = MARKUP.sub(' ', text.lower())
        return pattern.findall(text)
