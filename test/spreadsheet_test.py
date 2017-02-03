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

import datetime
import unittest

import hyou.client

import http_mocks


class SpreadsheetTest(unittest.TestCase):

    def setUp(self):
        self.api = hyou.client.API(http_mocks.ReplayHttp.get_instance())
        self.collection = hyou.client.Collection(self.api)
        self.spreadsheet = self.collection[
            '1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc']

    def test_worksheet_accessors(self):
        # iter()
        it = iter(self.spreadsheet)
        self.assertEqual('Sheet1', next(it))
        self.assertEqual('Sheet2', next(it))
        self.assertEqual('Sheet3', next(it))
        self.assertRaises(StopIteration, next, it)
        # len()
        self.assertEqual(3, len(self.spreadsheet))
        # keys()
        self.assertEqual(['Sheet1', 'Sheet2', 'Sheet3'],
                         self.spreadsheet.keys())
        # values()
        values = self.spreadsheet.values()
        self.assertEqual(3, len(values))
        self.assertEqual('Sheet1', values[0].title)
        self.assertEqual('Sheet2', values[1].title)
        self.assertEqual('Sheet3', values[2].title)
        # items()
        items = self.spreadsheet.items()
        self.assertEqual(3, len(items))
        self.assertEqual('Sheet1', items[0][0])
        self.assertEqual('Sheet1', items[0][1].title)
        self.assertEqual('Sheet2', items[1][0])
        self.assertEqual('Sheet2', items[1][1].title)
        self.assertEqual('Sheet3', items[2][0])
        self.assertEqual('Sheet3', items[2][1].title)
        # Indexing by an integer
        self.assertEqual('Sheet1', self.spreadsheet[0].title)
        self.assertEqual('Sheet2', self.spreadsheet[1].title)
        self.assertEqual('Sheet3', self.spreadsheet[2].title)
        # Indexing by a key
        self.assertEqual('Sheet1', self.spreadsheet['Sheet1'].title)
        self.assertEqual('Sheet2', self.spreadsheet['Sheet2'].title)
        self.assertEqual('Sheet3', self.spreadsheet['Sheet3'].title)

    def test_refresh(self):
        self.spreadsheet.refresh()

    def test_add_worksheet(self):
        worksheet = self.spreadsheet.add_worksheet('Sheet4', rows=2, cols=8)
        self.assertEqual('Sheet4', worksheet.title)
        self.assertEqual(2, worksheet.rows)
        self.assertEqual(8, worksheet.cols)

    def test_delete_worksheet(self):
        self.spreadsheet.delete_worksheet('Sheet3')

    def test_url(self):
        self.assertEqual(
            'https://docs.google.com/spreadsheets/d/'
            '1OB50n5vs3ZaLKgQ_BHkD7AGkNDMICo3jPXPQ8Y1_ekc/edit',
            self.spreadsheet.url)

    def test_title(self):
        self.assertEqual('Test Sheet', self.spreadsheet.title)

    def test_title_setter(self):
        self.spreadsheet.title = 'Yet Another Test Sheet'

    def test_updated(self):
        self.assertEqual(
            datetime.datetime(
                year=2017, month=2, day=3, hour=1, minute=25, second=31,
                microsecond=49000),
            self.spreadsheet.updated)
