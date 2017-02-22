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
import hyou.util

import http_mocks


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

    def test_title(self):
        self.assertEqual('Sheet1', self.worksheet1.title)

    def test_rows(self):
        self.assertEqual(2, self.worksheet1.rows)

    def test_cols(self):
        self.assertEqual(5, self.worksheet1.cols)

    def test_repr(self):
        self.assertEqual(str('Worksheet(key=0)'), repr(self.worksheet1))

    def test_view(self):
        self.worksheet1.view(start_row=3)
        self.worksheet1.view(end_row=-1)
        self.worksheet1.view(start_row=1, end_row=0)
        self.worksheet1.view(start_col=6)
        self.worksheet1.view(end_col=-1)
        self.worksheet1.view(start_col=1, end_col=0)


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
