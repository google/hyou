import unittest

import mox

import hyou.util


class LazyOrderedDictionaryTest(unittest.TestCase):
  def setUp(self):
    self.mox = mox.Mox()
    self.enumerator = self.mox.CreateMockAnything()
    self.constructor = self.mox.CreateMockAnything()
    self.dict = hyou.util.LazyOrderedDictionary(
        enumerator=self.enumerator, constructor=self.constructor)

  def tearDown(self):
    self.mox.UnsetStubs()
    self.mox.VerifyAll()

  def test_enumerate(self):
    self.enumerator().AndReturn(
        [('A', 'apple'), ('B', 'banana'), ('C', 'cinamon')])
    self.mox.ReplayAll()

    # iter()
    it = iter(self.dict)
    self.assertEqual('A', it.next())
    self.assertEqual('B', it.next())
    self.assertEqual('C', it.next())
    self.assertRaises(StopIteration, it.next)
    # len()
    self.assertEqual(3, len(self.dict))
    # keys()
    self.assertEqual(['A', 'B', 'C'], self.dict.keys())
    # values()
    self.assertEqual(['apple', 'banana', 'cinamon'], self.dict.values())
    # items()
    self.assertEqual(
        [('A', 'apple'), ('B', 'banana'), ('C', 'cinamon')],
        self.dict.items())
    # Indexing by an integer
    self.assertEqual('apple', self.dict[0])
    self.assertEqual('banana', self.dict[1])
    self.assertEqual('cinamon', self.dict[2])
    # Indexing by a key
    self.assertEqual('apple', self.dict['A'])
    self.assertEqual('banana', self.dict['B'])
    self.assertEqual('cinamon', self.dict['C'])

  def test_construct(self):
    self.constructor('A').AndReturn('apple')
    self.mox.ReplayAll()
    self.assertEqual('apple', self.dict['A'])

  def test_refresh(self):
    self.constructor('A').AndReturn('apple1')
    self.constructor('A').AndReturn('apple2')
    self.mox.ReplayAll()

    self.dict.refresh()
    self.assertEqual('apple1', self.dict['A'])
    self.assertEqual('apple1', self.dict['A'])
    self.dict.refresh()
    self.assertEqual('apple2', self.dict['A'])
    self.assertEqual('apple2', self.dict['A'])
    self.dict.refresh()

  def test_construct_then_enumerate(self):
    self.constructor('B').AndReturn('bacon')
    self.enumerator().AndReturn(
        [('A', 'apple'), ('B', 'banana'), ('C', 'cinamon')])
    self.mox.ReplayAll()

    self.assertEqual('bacon', self.dict['B'])
    self.assertEqual(['A', 'B', 'C'], self.dict.keys())
    self.assertEqual(['apple', 'bacon', 'cinamon'], self.dict.values())

  def test_enumerate_then_construct_unlisted(self):
    self.enumerator().AndReturn([('A', 'apple'), ('C', 'cinamon')])
    self.constructor('B').AndReturn('banana')
    self.mox.ReplayAll()

    self.assertEqual(['A', 'C'], self.dict.keys())
    self.assertEqual(['apple', 'cinamon'], self.dict.values())
    self.assertEqual('banana', self.dict['B'])
    self.assertEqual(['A', 'C', 'B'], self.dict.keys())
    self.assertEqual(['apple', 'cinamon', 'banana'], self.dict.values())

  def test_construct_then_enumerate_unlisted(self):
    self.constructor('B').AndReturn('banana')
    self.enumerator().AndReturn([('A', 'apple'), ('C', 'cinamon')])
    self.mox.ReplayAll()

    self.assertEqual('banana', self.dict['B'])
    self.assertEqual(['A', 'C', 'B'], self.dict.keys())
    self.assertEqual(['apple', 'cinamon', 'banana'], self.dict.values())
