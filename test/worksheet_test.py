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

import unittest

import hyou.api
import hyou.collection
from hyou import py3
import hyou.util

import http_mocks


class Dummy(object):

    def __str__(self):
        return py3.str_to_native_str('<dummy>')


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

    def test_read(self):
        self.assertEqual('honoka', self.worksheet1[0][0])
        self.assertEqual('eri', self.worksheet1[0][1])
        self.assertEqual('kotori', self.worksheet1[0][2])
        self.assertEqual('umi', self.worksheet1[0][3])
        self.assertEqual('rin', self.worksheet1[0][4])
        self.assertEqual('maki', self.worksheet1[1][0])
        self.assertEqual('nozomi', self.worksheet1[1][1])
        self.assertEqual('hanayo', self.worksheet1[1][2])
        self.assertEqual('niko', self.worksheet1[1][3])
        self.assertEqual('', self.worksheet1[1][4])

        # negative indexing
        self.assertEqual('kotori', self.worksheet1[-2][-3])

        # slicing
        t = self.worksheet1[:]
        self.assertEqual(2, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.worksheet1[1:]
        self.assertEqual(1, len(t))
        self.assertEqual('maki', t[0][0])
        t = self.worksheet1[:1]
        self.assertEqual(1, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.worksheet1[0:1]
        self.assertEqual(1, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.worksheet1[-1:]
        self.assertEqual(1, len(t))
        self.assertEqual('maki', t[0][0])
        t = self.worksheet1[:-1]
        self.assertEqual(1, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.worksheet1[-2:0]
        self.assertEqual(0, len(t))

        t = self.worksheet1[0][:]
        self.assertEqual(5, len(t))
        self.assertEqual('honoka', t[0])
        t = self.worksheet1[0][2:]
        self.assertEqual(3, len(t))
        self.assertEqual('kotori', t[0])
        t = self.worksheet1[0][:2]
        self.assertEqual(2, len(t))
        self.assertEqual('honoka', t[0])
        t = self.worksheet1[0][2:3]
        self.assertEqual(1, len(t))
        self.assertEqual('kotori', t[0])
        t = self.worksheet1[0][-3:]
        self.assertEqual(3, len(t))
        self.assertEqual('kotori', t[0])
        t = self.worksheet1[0][:-3]
        self.assertEqual(2, len(t))
        self.assertEqual('honoka', t[0])
        t = self.worksheet1[0][-3:0]
        self.assertEqual(0, len(t))

        # out of bounds
        with self.assertRaises(IndexError):
            self.worksheet1[0][5]
        with self.assertRaises(IndexError):
            self.worksheet1[0][-6]
        with self.assertRaises(IndexError):
            self.worksheet1[2][0]
        with self.assertRaises(IndexError):
            self.worksheet1[-3][0]

    def test_nonzero(self):
        self.assertFalse(self.worksheet1[0:0])
        self.assertFalse(self.worksheet1[0][0:0])
        self.assertFalse(
            self.worksheet1.view(
                start_row=0, end_row=0, start_col=0, end_col=0))

    def test_title(self):
        self.assertEqual('Sheet1', self.worksheet1.title)

    def test_rows(self):
        self.assertEqual(2, self.worksheet1.rows)

    def test_cols(self):
        self.assertEqual(5, self.worksheet1.cols)

    def test_len(self):
        self.assertEqual(2, len(self.worksheet1))
        self.assertEqual(5, len(self.worksheet1[0]))

    def test_iter(self):
        self.assertEqual(
            [['honoka', 'eri', 'kotori', 'umi', 'rin'],
             ['maki', 'nozomi', 'hanayo', 'niko', '']],
            list(self.worksheet1))

    def test_repr(self):
        self.assertEqual(
            repr([['honoka', 'eri', 'kotori', 'umi', 'rin'],
                  ['maki', 'nozomi', 'hanayo', 'niko', '']]),
            repr(self.worksheet1))

    def test_view(self):
        view = self.worksheet1.view()
        self.assertEqual(0, view.start_row)
        self.assertEqual(2, view.end_row)
        self.assertEqual(0, view.start_col)
        self.assertEqual(5, view.end_col)
        self.assertEqual(2, view.rows)
        self.assertEqual(5, view.cols)

        self.worksheet1.view(start_row=3)
        self.worksheet1.view(end_row=-1)
        self.worksheet1.view(start_row=1, end_row=0)
        self.worksheet1.view(start_col=6)
        self.worksheet1.view(end_col=-1)
        self.worksheet1.view(start_col=1, end_col=0)

        view = self.worksheet1.view(end_row=1, start_col=2)
        self.assertEqual(0, view.start_row)
        self.assertEqual(1, view.end_row)
        self.assertEqual(2, view.start_col)
        self.assertEqual(5, view.end_col)
        self.assertEqual(1, view.rows)
        self.assertEqual(3, view.cols)

        self.assertEqual('kotori', view[0][0])
        self.assertEqual('kotori', view[-1][-3])

        with self.assertRaises(IndexError):
            view[0][3]
        with self.assertRaises(IndexError):
            view[0][-4]
        with self.assertRaises(IndexError):
            view[1][0]
        with self.assertRaises(IndexError):
            view[2][0]


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

    def test_set_title(self):
        self.worksheet1.title = 'Sheet1'

    def test_set_size(self):
        self.worksheet1.set_size(2, 5)

    def test_set_rows(self):
        self.worksheet1.rows = 2

    def test_set_cols(self):
        self.worksheet1.cols = 5

    def test_write(self):
        self.worksheet1[1][3] = 'nicco'
        self.worksheet1[1][3] = 'nicco'
        self.worksheet1[1][3] = 'ni'
        self.worksheet1[0][-3] = 'chunchun'
        with self.assertRaises(IndexError):
            self.worksheet1[1][5] = '(*8*)'
        self.worksheet1.commit()

    def test_write_slice(self):
        self.worksheet1[0][3:2] = []
        self.worksheet1[0][:] = ['honoka', 'eri', 'kotori', 'umi', 'rin']
        self.worksheet1[1][0:-1] = ['maki', 'nozomi', 'hanayo', 'niko']
        with self.assertRaises(ValueError):
            self.worksheet1[1][:] = ['maki', 'nozomi', 'hanayo', 'niko']
        self.worksheet1[:] = [
            ['honoka', 'eri', 'kotori', 'umi', 'rin'],
            ['maki', 'nozomi', 'hanayo', 'niko', '']]
        with self.assertRaises(ValueError):
            self.worksheet1[:] = [
                ['honoka', 'eri', 'kotori', 'umi', 'rin'],
                ['maki', 'nozomi', 'hanayo', 'niko']]
        self.worksheet1.commit()

    def test_write_nonstr(self):
        self.worksheet1[0][0] = 28
        self.worksheet1[0][1] = 28.3
        self.worksheet1[0][2] = 'kotori-chan'
        with self.assertRaises(UnicodeDecodeError):
            self.worksheet1[0][3] = b'\xe6\xb5\xb7'
        self.worksheet1[0][4] = 'nya'
        self.worksheet1[1][0] = Dummy()
        self.worksheet1[1][4] = None
        self.worksheet1.commit()

    def test_write_with(self):
        with self.worksheet1:
            self.worksheet1[1][3] = 'nico'

    def test_refresh(self):
        self.assertEqual('honoka', self.worksheet1[0][0])

        self.worksheet1[0][0] = 'yukiho'
        self.assertEqual('yukiho', self.worksheet1[0][0])

        # Discard write operations
        self.worksheet1.refresh()

        self.assertEqual('honoka', self.worksheet1[0][0])
