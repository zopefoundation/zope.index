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
"""Set Options tests

$Id$
"""
from unittest import TestCase, main, makeSuite

import BTrees

from BTrees.IFBTree import IFBTree, IFBucket
from BTrees.LFBTree import LFBucket

from zope.index.text.setops import mass_weightedIntersection
from zope.index.text.setops import mass_weightedUnion

class TestSetOps(TestCase):

    def testEmptyLists(self):
        self.assertEqual(len(mass_weightedIntersection([])), 0)
        self.assertEqual(len(mass_weightedUnion([])), 0)

    def testEmptyListsHonorFamily(self):
        # family32
        t = mass_weightedIntersection([], BTrees.family32)
        self.assertEqual(len(t), 0)
        self.assertEqual(t.__class__, IFBucket)
        t = mass_weightedUnion([], BTrees.family32)
        self.assertEqual(len(t), 0)
        self.assertEqual(t.__class__, IFBucket)

        # family64
        t = mass_weightedIntersection([], BTrees.family64)
        self.assertEqual(len(t), 0)
        self.assertEqual(t.__class__, LFBucket)
        t = mass_weightedUnion([], BTrees.family64)
        self.assertEqual(len(t), 0)
        self.assertEqual(t.__class__, LFBucket)

    def testIdentity(self):
        t = IFBTree([(1, 2)])
        b = IFBucket([(1, 2)])
        for x in t, b:
            for func in mass_weightedUnion, mass_weightedIntersection:
                result = func([(x, 1)])
                self.assertEqual(len(result), 1)
                self.assertEqual(list(result.items()), list(x.items()))

    def testScalarMultiply(self):
        t = IFBTree([(1, 2), (2, 3), (3, 4)])
        allkeys = [1, 2, 3]
        b = IFBucket(t)
        for x in t, b:
            self.assertEqual(list(x.keys()), allkeys)
            for func in mass_weightedUnion, mass_weightedIntersection:
                for factor in 0, 1, 5, 10:
                    result = func([(x, factor)])
                    self.assertEqual(allkeys, list(result.keys()))
                    for key in x.keys():
                        self.assertEqual(x[key] * factor, result[key])

    def testPairs(self):
        t1 = IFBTree([(1, 10), (3, 30), (7, 70)])
        t2 = IFBTree([(3, 30), (5, 50), (7, 7), (9, 90)])
        allkeys = [1, 3, 5, 7, 9]
        b1 = IFBucket(t1)
        b2 = IFBucket(t2)
        for x in t1, t2, b1, b2:
            for key in x.keys():
                self.assertEqual(key in allkeys, 1)
            for y in t1, t2, b1, b2:
                for w1, w2 in (0, 0), (1, 10), (10, 1), (2, 3):
                    # Test the union.
                    expected = []
                    for key in allkeys:
                        if x.has_key(key) or y.has_key(key):
                            result = x.get(key, 0) * w1 + y.get(key, 0) * w2
                            expected.append((key, result))
                    expected.sort()
                    got = mass_weightedUnion([(x, w1), (y, w2)])
                    self.assertEqual(expected, list(got.items()))
                    got = mass_weightedUnion([(y, w2), (x, w1)])
                    self.assertEqual(expected, list(got.items()))

                    # Test the intersection.
                    expected = []
                    for key in allkeys:
                        if x.has_key(key) and y.has_key(key):
                            result = x[key] * w1 + y[key] * w2
                            expected.append((key, result))
                    expected.sort()
                    got = mass_weightedIntersection([(x, w1), (y, w2)])
                    self.assertEqual(expected, list(got.items()))
                    got = mass_weightedIntersection([(y, w2), (x, w1)])
                    self.assertEqual(expected, list(got.items()))

    def testMany(self):
        import random
        N = 15  # number of IFBTrees to feed in
        L = []
        commonkey = N * 1000
        allkeys = {commonkey: 1}
        for i in range(N):
            t = IFBTree()
            t[commonkey] = i
            for j in range(N-i):
                key = i + j
                allkeys[key] = 1
                t[key] = N*i + j
            L.append((t, i+1))
        random.shuffle(L)
        allkeys = allkeys.keys()
        allkeys.sort()

        # Test the union.
        expected = []
        for key in allkeys:
            sum = 0
            for t, w in L:
                if t.has_key(key):
                    sum += t[key] * w
            expected.append((key, sum))
        # print 'union', expected
        got = mass_weightedUnion(L)
        self.assertEqual(expected, list(got.items()))

        # Test the intersection.
        expected = []
        for key in allkeys:
            sum = 0
            for t, w in L:
                if t.has_key(key):
                    sum += t[key] * w
                else:
                    break
            else:
                # We didn't break out of the loop so it's in the intersection.
                expected.append((key, sum))
        # print 'intersection', expected
        got = mass_weightedIntersection(L)
        self.assertEqual(expected, list(got.items()))

def test_suite():
    return makeSuite(TestSetOps)

if __name__=="__main__":
    main(defaultTest='test_suite')
