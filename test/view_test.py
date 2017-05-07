# Copyright 2017 Google Inc. All rights reserved
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

import unittest

import hyou.api
import hyou.collection
from hyou import py3
import hyou.util

import http_mocks


class Dummy(object):

    def __str__(self):
        return py3.str_to_native_str('<dummy>', encoding='ascii')


class WorksheetReadOnlyTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = hyou.api.API(
            http_mocks.ReplayHttp('unittest-sheets.json'),
            discovery=False)

    def setUp(self):
        self.collection = hyou.collection.Collection(self.api)
        self.spreadsheet = self.collection[
            '18OLN5A2SSKAeYLXw4SnZxU1yRJnMdf_ZCjc0D2UdhX8']
        self.worksheet1 = self.spreadsheet['Sheet1']
        self.view = self.worksheet1.view()

    def test_read(self):
        self.assertEqual('honoka', self.view[0][0])
        self.assertEqual('eri', self.view[0][1])
        self.assertEqual('kotori', self.view[0][2])
        self.assertEqual('umi', self.view[0][3])
        self.assertEqual('rin', self.view[0][4])
        self.assertEqual('maki', self.view[1][0])
        self.assertEqual('nozomi', self.view[1][1])
        self.assertEqual('hanayo', self.view[1][2])
        self.assertEqual('niko', self.view[1][3])
        self.assertEqual('', self.view[1][4])

        # negative indexing
        self.assertEqual('kotori', self.view[-2][-3])

        # slicing
        t = self.view[:]
        self.assertEqual(2, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.view[1:]
        self.assertEqual(1, len(t))
        self.assertEqual('maki', t[0][0])
        t = self.view[:1]
        self.assertEqual(1, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.view[0:1]
        self.assertEqual(1, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.view[-1:]
        self.assertEqual(1, len(t))
        self.assertEqual('maki', t[0][0])
        t = self.view[:-1]
        self.assertEqual(1, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.view[-2:0]
        self.assertEqual(0, len(t))

        t = self.view[0][:]
        self.assertEqual(5, len(t))
        self.assertEqual('honoka', t[0])
        t = self.view[0][2:]
        self.assertEqual(3, len(t))
        self.assertEqual('kotori', t[0])
        t = self.view[0][:2]
        self.assertEqual(2, len(t))
        self.assertEqual('honoka', t[0])
        t = self.view[0][2:3]
        self.assertEqual(1, len(t))
        self.assertEqual('kotori', t[0])
        t = self.view[0][-3:]
        self.assertEqual(3, len(t))
        self.assertEqual('kotori', t[0])
        t = self.view[0][:-3]
        self.assertEqual(2, len(t))
        self.assertEqual('honoka', t[0])
        t = self.view[0][-3:0]
        self.assertEqual(0, len(t))

        # out of bounds
        with self.assertRaises(IndexError):
            self.view[0][5]
        with self.assertRaises(IndexError):
            self.view[0][-6]
        with self.assertRaises(IndexError):
            self.view[2][0]
        with self.assertRaises(IndexError):
            self.view[-3][0]

    def test_nonzero(self):
        self.assertTrue(self.view[0:1])
        self.assertFalse(self.view[0:0])
        self.assertTrue(self.view[0][0:1])
        self.assertFalse(self.view[0][0:0])

    def test_rows(self):
        self.assertEqual(2, self.worksheet1.rows)

    def test_cols(self):
        self.assertEqual(5, self.worksheet1.cols)

    def test_len(self):
        self.assertEqual(2, len(self.view))
        self.assertEqual(5, len(self.view[0]))

    def test_iter(self):
        self.assertEqual(
            [['honoka', 'eri', 'kotori', 'umi', 'rin'],
             ['maki', 'nozomi', 'hanayo', 'niko', '']],
            list(self.view))

    def test_repr(self):
        self.assertEqual(
            str('View(%r)' %
                [['honoka', 'eri', 'kotori', 'umi', 'rin'],
                 ['maki', 'nozomi', 'hanayo', 'niko', '']]),
            repr(self.view))

    def test_properties(self):
        self.assertEqual(0, self.view.start_row)
        self.assertEqual(2, self.view.end_row)
        self.assertEqual(0, self.view.start_col)
        self.assertEqual(5, self.view.end_col)
        self.assertEqual(2, self.view.rows)
        self.assertEqual(5, self.view.cols)


class WorksheetReadWriteTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = hyou.api.API(
            http_mocks.ReplayHttp('unittest-sheets.json'),
            discovery=False)

    def setUp(self):
        self.collection = hyou.collection.Collection(self.api)
        self.spreadsheet = self.collection[
            '1z5eYrVoLP-RUWdzeqUShRc2VPFX0SUCTlHMmUS0K8Lo']
        self.worksheet1 = self.spreadsheet['Sheet1']
        self.view = self.worksheet1.view()

    def test_write(self):
        self.view[1][3] = 'nicco'
        self.view[1][3] = 'nicco'
        self.view[1][3] = 'ni'
        self.view[0][-3] = 'chunchun'
        with self.assertRaises(IndexError):
            self.view[1][5] = '(*8*)'
        self.view.commit()

    def test_write_slice(self):
        self.view[0][3:2] = []
        self.view[0][:] = ['honoka', 'eri', 'kotori', 'umi', 'rin']
        self.view[1][0:-1] = ['maki', 'nozomi', 'hanayo', 'niko']
        with self.assertRaises(ValueError):
            self.view[1][:] = ['maki', 'nozomi', 'hanayo', 'niko']
        self.view[:] = [
            ['honoka', 'eri', 'kotori', 'umi', 'rin'],
            ['maki', 'nozomi', 'hanayo', 'niko', '']]
        with self.assertRaises(ValueError):
            self.view[:] = [
                ['honoka', 'eri', 'kotori', 'umi', 'rin'],
                ['maki', 'nozomi', 'hanayo', 'niko']]
        self.view.commit()

    def test_write_nonstr(self):
        self.view[0][0] = 28
        self.view[0][1] = 28.3
        self.view[0][2] = 'kotori-chan'
        with self.assertRaises(UnicodeDecodeError):
            self.view[0][3] = b'\xe6\xb5\xb7'
        self.view[0][4] = 'nya'
        self.view[1][0] = Dummy()
        self.view[1][4] = None
        self.view.commit()

    def test_refresh(self):
        self.assertEqual('honoka', self.view[0][0])

        self.view[0][0] = 'yukiho'
        self.assertEqual('yukiho', self.view[0][0])

        # Discard write operations
        self.view.refresh()

        self.assertEqual('honoka', self.view[0][0])
