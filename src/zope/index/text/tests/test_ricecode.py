"""
Tests for ricecode.py

"""
import unittest

from zope.index.text.ricecode import RiceCode
from zope.index.text.ricecode import decode_deltas
from zope.index.text.ricecode import encode
from zope.index.text.ricecode import encode_deltas
from zope.index.text.ricecode import pickle_efficiency


class TestRiceCode(unittest.TestCase):

    def test_random(self):
        import random
        for size in [1, 10, 20, 50, 100, 200]:
            l_ = [random.randint(1, size) for i in range(50)]
            c = encode(random.randint(1, 16), l_)
            self.assertEqual(c.tolist(), l_)
        for size in [1, 10, 20, 50, 100, 200]:
            l_ = list(
                range(
                    random.randint(
                        1,
                        size),
                    size +
                    random.randint(
                        1,
                        size)))
            l_0, deltas = encode_deltas(l_)
            l2 = decode_deltas(l_0, deltas)
            self.assertEqual(l_, l2)

    def test_encode_deltas_one_element(self):
        self.assertEqual(('foo', []),
                         encode_deltas(['foo']))

    def test_decode_deltas_one_element(self):
        self.assertEqual(['foo'],
                         decode_deltas('foo', []))

    def test_pickle_efficiency(self):
        # This is random data so it's hard to say what wins
        # and what loses.
        results = pickle_efficiency(sizes=(10, 20), elt_ranges=(10, 20))
        self.assertEqual(3, len(results))

    def test_bit_range(self):
        with self.assertRaises(ValueError):
            RiceCode(-1)
        with self.assertRaises(ValueError):
            RiceCode(17)

    def test_length(self):
        code = RiceCode(6)
        self.assertEqual(0, len(code))
        self.assertEqual(0, len(code.bits))

        code.append(1)
        self.assertEqual(1, len(code))
        self.assertEqual(7, len(code.bits))

    def test_append_invalid(self):
        with self.assertRaises(ValueError):
            RiceCode(6).append(0)

    def test_pickle(self):
        import pickle
        code = RiceCode(6)
        code.append(1)

        code2 = pickle.loads(pickle.dumps(code))

        self.assertEqual(code.m, code2.m)
        self.assertEqual(code.tostring(), code2.tostring())

        # But length is not preserved
        self.assertEqual(1, len(code))
        self.assertEqual(0, len(code2))
