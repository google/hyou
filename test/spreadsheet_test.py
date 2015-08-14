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

import datetime
import unittest

import gdata.spreadsheets.client
import mox

import hyou.client


class FakeSpreadsheetTitleFeed(object):
  def __init__(self, title):
    self.text = title


class FakeSpreadsheetUpdatedFeed(object):
  def __init__(self):
    self.text = '2015-08-11T12:34:56.789Z'


class FakeSpreadsheetFeed(object):
  def __init__(self, title):
    self.title = FakeSpreadsheetTitleFeed(title)
    self.updated = FakeSpreadsheetUpdatedFeed()


class FakeWorksheetFeed(object):
  def __init__(self, key):
    self._key = key

  def get_worksheet_id(self):
    return self._key


class FakeWorksheetsFeed(object):
  def __init__(self, entries):
    self.entry = entries


class SpreadsheetTest(unittest.TestCase):
  def setUp(self):
    self.mox = mox.Mox()
    self.mox.StubOutClassWithMocks(hyou.client, 'Worksheet')
    self.client = self.mox.CreateMock(
        gdata.spreadsheets.client.SpreadsheetsClient)
    self.drive = self.mox.CreateMockAnything()
    entry = FakeSpreadsheetFeed('Cinamon')
    self.spreadsheet = hyou.client.Spreadsheet(
        None, self.client, self.drive, 'cinamon', entry)

  def tearDown(self):
    self.mox.UnsetStubs()
    self.mox.VerifyAll()

  def set_enumerator_expectations(self):
    sheet1_feed = FakeWorksheetFeed('s1')
    sheet2_feed = FakeWorksheetFeed('s2')
    sheet3_feed = FakeWorksheetFeed('s3')
    feed = FakeWorksheetsFeed([sheet1_feed, sheet2_feed, sheet3_feed])

    self.client.get_worksheets('cinamon').AndReturn(feed)
    sheet1 = hyou.client.Worksheet(
        self.spreadsheet, self.client, 's1', sheet1_feed)
    sheet1.key = 's1'
    sheet1.title = 'Sheet1'
    sheet2 = hyou.client.Worksheet(
        self.spreadsheet, self.client, 's2', sheet2_feed)
    sheet2.key = 's2'
    sheet2.title = 'Sheet2'
    sheet3 = hyou.client.Worksheet(
        self.spreadsheet, self.client, 's3', sheet3_feed)
    sheet3.key = 's3'
    sheet3.title = 'Sheet3'
    return (sheet1, sheet2, sheet3)

  def set_refresh_expectations(self):
    self.client.get_feed(
        hyou.client.SPREADSHEET_URL % 'cinamon',
        desired_class=gdata.spreadsheets.data.Spreadsheet)

  def test_worksheet_accessors(self):
    sheet1, sheet2, sheet3 = self.set_enumerator_expectations()
    self.mox.ReplayAll()

    # iter()
    it = iter(self.spreadsheet)
    self.assertEqual('Sheet1', it.next())
    self.assertEqual('Sheet2', it.next())
    self.assertEqual('Sheet3', it.next())
    self.assertRaises(StopIteration, it.next)
    # len()
    self.assertEqual(3, len(self.spreadsheet))
    # keys()
    self.assertEqual(['Sheet1', 'Sheet2', 'Sheet3'], self.spreadsheet.keys())
    # values()
    self.assertEqual([sheet1, sheet2, sheet3], self.spreadsheet.values())
    # items()
    self.assertEqual(
        [('Sheet1', sheet1), ('Sheet2', sheet2), ('Sheet3', sheet3)],
        self.spreadsheet.items())
    # Indexing by an integer
    self.assertEqual(sheet1, self.spreadsheet[0])
    self.assertEqual(sheet2, self.spreadsheet[1])
    self.assertEqual(sheet3, self.spreadsheet[2])
    # Indexing by a key
    self.assertEqual(sheet1, self.spreadsheet['Sheet1'])
    self.assertEqual(sheet2, self.spreadsheet['Sheet2'])
    self.assertEqual(sheet3, self.spreadsheet['Sheet3'])

  def test_refresh(self):
    self.set_refresh_expectations()

    self.mox.ReplayAll()

    self.spreadsheet.refresh()

  def test_add_worksheet(self):
    self.client.add_worksheet('cinamon', 'Sheet3', rows=2, cols=8)
    self.set_refresh_expectations()
    sheet1, sheet2, sheet3 = self.set_enumerator_expectations()

    self.mox.ReplayAll()

    self.assertEqual(
        sheet3, self.spreadsheet.add_worksheet('Sheet3', rows=2, cols=8))

  def test_delete_worksheet(self):
    self.set_enumerator_expectations()
    self.client.delete(
        gdata.spreadsheets.client.WORKSHEET_URL % ('cinamon', 's3'),
        force=True)
    self.set_refresh_expectations()

    self.mox.ReplayAll()

    self.spreadsheet.delete_worksheet('Sheet3')

  def test_url(self):
    self.assertEqual(
        'https://docs.google.com/spreadsheets/d/cinamon/edit',
        self.spreadsheet.url)

  def test_title(self):
    self.assertEqual('Cinamon', self.spreadsheet.title)

  def test_title_setter(self):
    files = self.mox.CreateMockAnything()
    self.drive.files().AndReturn(files)
    executor = self.mox.CreateMockAnything()
    files.update(fileId='cinamon', body={'title': 'Lemon'}).AndReturn(executor)
    executor.execute().AndReturn({})
    self.set_refresh_expectations()

    self.mox.ReplayAll()

    self.spreadsheet.title = 'Lemon'

  def test_updated(self):
    self.assertEqual(
        datetime.datetime(
            year=2015, month=8, day=11, hour=12, minute=34, second=56,
            microsecond=789000),
        self.spreadsheet.updated)
