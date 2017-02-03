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


class WorksheetTest(unittest.TestCase):

    def setUp(self):
        self.api = hyou.client.API(http_mocks.ReplayHttp.get_instance())
        self.collection = hyou.client.Collection(self.api)
        self.spreadsheet = self.collection[
            '1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc']
        self.worksheet = self.spreadsheet['Sheet1']

    def test_read(self):
        self.assertEqual('honoka', self.worksheet[0][0])
        self.assertEqual('eri', self.worksheet[0][1])
        self.assertEqual('kotori', self.worksheet[0][2])
        self.assertEqual('umi', self.worksheet[0][3])
        self.assertEqual('rin', self.worksheet[0][4])
        self.assertEqual('maki', self.worksheet[1][0])
        self.assertEqual('nozomi', self.worksheet[1][1])
        self.assertEqual('hanayo', self.worksheet[1][2])
        self.assertEqual('niko', self.worksheet[1][3])
        self.assertEqual('', self.worksheet[1][4])

        # negative indexing
        self.assertEqual('kotori', self.worksheet[-2][-3])

        # slicing
        t = self.worksheet[:]
        self.assertEqual(2, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.worksheet[1:]
        self.assertEqual(1, len(t))
        self.assertEqual('maki', t[0][0])
        t = self.worksheet[:1]
        self.assertEqual(1, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.worksheet[0:1]
        self.assertEqual(1, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.worksheet[-1:]
        self.assertEqual(1, len(t))
        self.assertEqual('maki', t[0][0])
        t = self.worksheet[:-1]
        self.assertEqual(1, len(t))
        self.assertEqual('honoka', t[0][0])
        t = self.worksheet[-2:0]
        self.assertEqual(0, len(t))

        t = self.worksheet[0][:]
        self.assertEqual(5, len(t))
        self.assertEqual('honoka', t[0])
        t = self.worksheet[0][2:]
        self.assertEqual(3, len(t))
        self.assertEqual('kotori', t[0])
        t = self.worksheet[0][:2]
        self.assertEqual(2, len(t))
        self.assertEqual('honoka', t[0])
        t = self.worksheet[0][2:3]
        self.assertEqual(1, len(t))
        self.assertEqual('kotori', t[0])
        t = self.worksheet[0][-3:]
        self.assertEqual(3, len(t))
        self.assertEqual('kotori', t[0])
        t = self.worksheet[0][:-3]
        self.assertEqual(2, len(t))
        self.assertEqual('honoka', t[0])
        t = self.worksheet[0][-3:0]
        self.assertEqual(0, len(t))

        # out of bounds
        self.assertRaises(IndexError, lambda: self.worksheet[0][5])
        self.assertRaises(IndexError, lambda: self.worksheet[0][-6])
        self.assertRaises(IndexError, lambda: self.worksheet[2][0])
        self.assertRaises(IndexError, lambda: self.worksheet[-3][0])

    def test_write(self):
        self.worksheet.commit()  # empty commit does nothing
        self.worksheet[1][3] = 'nicco'
        self.worksheet[1][3] = 'nicco'
        self.worksheet[1][3] = 'ni'
        self.worksheet[0][-3] = 'chunchun'
        self.assertRaises(
            IndexError, self.worksheet[1].__setitem__, 5, '(*8*)')
        self.worksheet.commit()

    def test_write_slice(self):
        self.worksheet[0][3:2] = []
        self.worksheet[0][:] = ['honoka', 'eri', 'kotori', 'umi', 'rin']
        self.worksheet[1][0:-1] = ['maki', 'nozomi', 'hanayo', 'niko']
        self.assertRaises(
            ValueError,
            self.worksheet[1].__setitem__,
            slice(None),
            ['maki', 'nozomi', 'hanayo', 'niko'])
        self.worksheet.commit()

    def test_write_nonstr(self):
        self.worksheet.commit()  # empty commit does nothing
        self.worksheet[0][0] = 28
        self.worksheet[0][1] = 28.3
        self.worksheet[0][2] = 'kotori-chan'
        self.assertRaises(
            UnicodeDecodeError, self.worksheet[0].__setitem__, 3,
            b'\xe6\xb5\xb7')
        self.worksheet[0][4] = 'nya'
        self.assertRaises(IndexError, self.worksheet[
                          0].__setitem__, 5, '(*8*)')
        self.worksheet[1][4] = None
        self.worksheet.commit()

    def test_write_with(self):
        with self.worksheet:
            self.worksheet[1][3] = 'nico'

    def test_nonzero(self):
        self.assertFalse(self.worksheet[0:0])
        self.assertFalse(self.worksheet[0][0:0])
        self.assertFalse(
            self.worksheet.view(
                start_row=0, end_row=0, start_col=0, end_col=0))

    def test_refresh(self):
        self.assertEqual('honoka', self.worksheet[0][0])
        self.worksheet[0][0] = 'yukiho'
        self.assertEqual('yukiho', self.worksheet[0][0])

        # Discard write operations
        self.worksheet.refresh()

        self.assertEqual('honoka', self.worksheet[0][0])

    def test_set_size(self):
        self.worksheet.set_size(7, 8)
        self.assertEqual(7, self.worksheet.rows)
        self.assertEqual(8, self.worksheet.cols)
        self.assertEqual(7, len(self.worksheet))
        self.assertEqual(8, len(self.worksheet[0]))

    def test_title(self):
        self.assertEqual('Sheet1', self.worksheet.title)

    def test_title_setter(self):
        self.worksheet.title = 'Summary'
        self.assertEqual('Summary', self.worksheet.title)

    def test_rows(self):
        self.assertEqual(2, self.worksheet.rows)

    def test_rows_setter(self):
        self.worksheet.rows = 7
        self.assertEqual(7, self.worksheet.rows)
        self.assertEqual(5, self.worksheet.cols)

    def test_cols(self):
        self.assertEqual(5, self.worksheet.cols)

    def test_cols_setter(self):
        self.worksheet.cols = 8
        self.assertEqual(2, self.worksheet.rows)
        self.assertEqual(8, self.worksheet.cols)

    def test_len(self):
        self.assertEqual(2, len(self.worksheet))
        self.assertEqual(5, len(self.worksheet[0]))

    def test_iter(self):
        it = iter(self.worksheet)
        self.assertEqual(['honoka', 'eri', 'kotori', 'umi', 'rin'], next(it))
        self.assertEqual(['maki', 'nozomi', 'hanayo', 'niko', ''], next(it))
        self.assertRaises(StopIteration, next, it)

    def test_repr(self):
        self.assertEqual(
            repr([['honoka', 'eri', 'kotori', 'umi', 'rin'],
                  ['maki', 'nozomi', 'hanayo', 'niko', '']]),
            repr(self.worksheet))

    def test_view(self):
        view = self.worksheet.view()
        self.assertEqual(0, view.start_row)
        self.assertEqual(2, view.end_row)
        self.assertEqual(0, view.start_col)
        self.assertEqual(5, view.end_col)
        self.assertEqual(2, view.rows)
        self.assertEqual(5, view.cols)

        self.assertRaises(IndexError, self.worksheet.view, start_row=3)
        self.assertRaises(IndexError, self.worksheet.view, end_row=-1)
        self.assertRaises(IndexError, self.worksheet.view,
                          start_row=1, end_row=0)
        self.assertRaises(IndexError, self.worksheet.view, start_col=6)
        self.assertRaises(IndexError, self.worksheet.view, end_col=-1)
        self.assertRaises(IndexError, self.worksheet.view,
                          start_col=1, end_col=0)

        view = self.worksheet.view(end_row=1, start_col=2)
        self.assertEqual(0, view.start_row)
        self.assertEqual(1, view.end_row)
        self.assertEqual(2, view.start_col)
        self.assertEqual(5, view.end_col)
        self.assertEqual(1, view.rows)
        self.assertEqual(3, view.cols)

        self.assertEqual('kotori', view[0][0])
        self.assertEqual('kotori', view[-1][-3])

        self.assertRaises(IndexError, lambda: view[0][3])
        self.assertRaises(IndexError, lambda: view[0][-4])
        self.assertRaises(IndexError, lambda: view[1][0])
        self.assertRaises(IndexError, lambda: view[-2][0])
