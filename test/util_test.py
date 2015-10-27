# Copyright 2015 Google Inc. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

  def test_no_constructor_indexing(self):
    self.constructor('A').AndReturn(None)
    self.enumerator().AndReturn([('A', 'apple')])
    self.mox.ReplayAll()
    self.assertEqual('apple', self.dict['A'])

  def test_no_constructor_indexing_miss(self):
    self.constructor('A').AndReturn(None)
    self.enumerator().AndReturn([('B', 'banana')])
    self.mox.ReplayAll()
    self.assertRaises(KeyError, self.dict.__getitem__, 'A')

  def test_get(self):
    self.enumerator().AndReturn([('A', 'apple')])
    self.constructor('B').AndReturn(None)
    self.mox.ReplayAll()
    list(self.dict)
    self.assertEqual('apple', self.dict.get('A', 'missing'))
    self.assertEqual('missing', self.dict.get('B', 'missing'))


class PseudoList(hyou.util.CustomMutableFixedList):
  def __init__(self, real_list):
    self.real_list = real_list

  def __getitem__(self, i):
    return self.real_list[i]

  def __iter__(self):
    return iter(self.real_list)

  def __len__(self):
    return len(self.real_list)

  def __setitem__(self, i, value):
    self.real_list[i] = value


class CustomMutableFixedListTest(unittest.TestCase):
  def setUp(self):
    self.list = PseudoList(['apple', 'banana', 'cinamon', 'apple'])

  def test_ordering(self):
    # __eq__
    self.assertTrue(['apple', 'banana', 'cinamon', 'apple'] == self.list)
    self.assertFalse(['apple', 'banana', 'cinamon', 'lemon'] == self.list)
    self.assertFalse(['apple', 'banana', 'cinamon'] == self.list)
    # __ne__
    self.assertFalse(['apple', 'banana', 'cinamon', 'apple'] != self.list)
    self.assertTrue(['apple', 'banana', 'cinamon', 'lemon'] != self.list)
    self.assertTrue(['apple', 'banana', 'cinamon'] != self.list)
    # __lt__
    self.assertFalse(['apple', 'banana', 'cinamon', 'apple'] < self.list)
    self.assertTrue(['apple', 'bacon', 'cinamon', 'apple'] < self.list)
    self.assertFalse(['apple', 'lemon', 'cinamon', 'apple'] < self.list)
    self.assertTrue(['apple', 'banana', 'cinamon'] < self.list)
    self.assertFalse(
        ['apple', 'banana', 'cinamon', 'apple', 'lemon'] < self.list)
    # __le__
    self.assertTrue(['apple', 'banana', 'cinamon', 'apple'] <= self.list)
    self.assertTrue(['apple', 'bacon', 'cinamon', 'apple'] <= self.list)
    self.assertFalse(['apple', 'lemon', 'cinamon', 'apple'] <= self.list)
    self.assertTrue(['apple', 'banana', 'cinamon'] <= self.list)
    self.assertFalse(
        ['apple', 'banana', 'cinamon', 'apple', 'lemon'] <= self.list)
    # __gt__
    self.assertFalse(['apple', 'banana', 'cinamon', 'apple'] > self.list)
    self.assertFalse(['apple', 'bacon', 'cinamon', 'apple'] > self.list)
    self.assertTrue(['apple', 'lemon', 'cinamon', 'apple'] > self.list)
    self.assertFalse(['apple', 'banana', 'cinamon'] > self.list)
    self.assertTrue(
        ['apple', 'banana', 'cinamon', 'apple', 'lemon'] > self.list)
    # __ge__
    self.assertTrue(['apple', 'banana', 'cinamon', 'apple'] >= self.list)
    self.assertFalse(['apple', 'bacon', 'cinamon', 'apple'] >= self.list)
    self.assertTrue(['apple', 'lemon', 'cinamon', 'apple'] >= self.list)
    self.assertFalse(['apple', 'banana', 'cinamon'] >= self.list)
    self.assertTrue(
        ['apple', 'banana', 'cinamon', 'apple', 'lemon'] >= self.list)

  def test_contains(self):
    self.assertTrue('apple' in self.list)
    self.assertFalse('bacon' in self.list)

  def test_index(self):
    self.assertEqual(0, self.list.index('apple'))
    self.assertRaises(ValueError, self.list.index, 'bacon')

  def test_count(self):
    self.assertEqual(2, self.list.count('apple'))
    self.assertEqual(1, self.list.count('banana'))
    self.assertEqual(0, self.list.count('bacon'))

  def test_reverse(self):
    self.list.reverse()
    self.assertEqual('apple', self.list[0])
    self.assertEqual('cinamon', self.list[1])
    self.assertEqual('banana', self.list[2])
    self.assertEqual('apple', self.list[3])

  def test_sort(self):
    self.list.sort()
    self.assertEqual('apple', self.list[0])
    self.assertEqual('apple', self.list[1])
    self.assertEqual('banana', self.list[2])
    self.assertEqual('cinamon', self.list[3])

  def test_unsupported(self):
    self.assertRaises(NotImplementedError, self.list.__delitem__, 0)
    self.assertRaises(NotImplementedError, self.list.append, 'lemon')
    self.assertRaises(NotImplementedError, self.list.extend, ['lemon'])
    self.assertRaises(NotImplementedError, self.list.insert, 0, 'lemon')
    self.assertRaises(NotImplementedError, self.list.pop)
    self.assertRaises(NotImplementedError, self.list.remove, 'apple')
