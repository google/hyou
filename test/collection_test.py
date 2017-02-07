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

from __future__ import (
    absolute_import, division, print_function, unicode_literals)
from builtins import (  # noqa: F401
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next,
    object, oct, open, pow, range, round, str, super, zip)

import unittest

import hyou.client

import http_mocks


class CollectionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = hyou.client.API(http_mocks.ReplayHttp(), discovery=False)

    def setUp(self):
        self.collection = hyou.client.Collection(self.api)

    def test_discovery(self):
        pass

    def test_accessors_with_constructor(self):
        # Indexing by a key
        self.collection['1ZYeIFccacgHkL0TPfdgXiMfPCuEEWUtbhXvaB9HBDzQ']

    def test_accessors_with_enumerator(self):
        # iter()
        it = iter(self.collection)
        self.assertEqual(
            '1Lm8oYdqQWV0nweNql4S_g_iUhpVxJHXw0lwn5rsU2zM', next(it))
        self.assertEqual(
            '1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc', next(it))
        self.assertRaises(StopIteration, next, it)
        # len()
        self.assertEqual(2, len(self.collection))
        # keys()
        self.assertEqual(
            ['1Lm8oYdqQWV0nweNql4S_g_iUhpVxJHXw0lwn5rsU2zM',
             '1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc'],
            self.collection.keys())
        # values()
        values = self.collection.values()
        self.assertEqual(2, len(values))
        self.assertEqual(
            '1Lm8oYdqQWV0nweNql4S_g_iUhpVxJHXw0lwn5rsU2zM', values[0].key)
        self.assertEqual(
            '1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc', values[1].key)
        # items()
        items = self.collection.items()
        self.assertEqual(2, len(items))
        self.assertEqual(
            '1Lm8oYdqQWV0nweNql4S_g_iUhpVxJHXw0lwn5rsU2zM', items[0][0])
        self.assertEqual(
            '1Lm8oYdqQWV0nweNql4S_g_iUhpVxJHXw0lwn5rsU2zM', items[0][1].key)
        self.assertEqual(
            '1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc', items[1][0])
        self.assertEqual(
            '1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc', items[1][1].key)
        # Indexing by an integer
        self.assertEqual(
            '1Lm8oYdqQWV0nweNql4S_g_iUhpVxJHXw0lwn5rsU2zM',
            self.collection[0].key)
        self.assertEqual(
            '1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc',
            self.collection[1].key)
        # Indexing by a key
        self.assertEqual(
            '1Lm8oYdqQWV0nweNql4S_g_iUhpVxJHXw0lwn5rsU2zM',
            self.collection['1Lm8oYdqQWV0nweNql4S_g_iUhpVxJHXw0lwn5rsU2zM']
            .key)
        self.assertEqual(
            '1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc',
            self.collection['1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc']
            .key)

    def test_create_spreadsheet(self):
        self.collection.create_spreadsheet('Cinnamon', rows=2, cols=8)
