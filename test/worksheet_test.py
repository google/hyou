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

import gdata.spreadsheets.client
import mox

import hyou.client


class Struct(object):
  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

  def __eq__(self, other):
    return self.__dict__ == other.__dict__


class FakeWorksheetFeed(object):
  def __init__(self, title, row_count, col_count):
    self.title = Struct(text=title)
    self.row_count = Struct(text=row_count)
    self.col_count = Struct(text=col_count)

  def __eq__(self, other):
    return self.__dict__ == other.__dict__


class FakeCellsFeed(object):
  def __init__(self, cells):
    self.entry = []
    for row, col, input_value in cells:
      self.entry.append(
          Struct(cell=Struct(row=row, col=col, input_value=input_value)))


class FakeSpreadsheet(object):
  def __init__(self, key):
    self.key = key


class WorksheetTest(unittest.TestCase):
  def setUp(self):
    self.mox = mox.Mox()
    self.client = self.mox.CreateMock(
        gdata.spreadsheets.client.SpreadsheetsClient)
    self.worksheet = hyou.client.Worksheet(
        FakeSpreadsheet('cinamon'),
        self.client,
        's1',
        FakeWorksheetFeed('Sheet1', '2', '5'))

  def tearDown(self):
    self.mox.UnsetStubs()
    self.mox.VerifyAll()

  def set_read_expectations(self):
    self.client.get_cells(
        'cinamon', 's1',
        query=mox.Func(
            lambda query:
                isinstance(query, gdata.spreadsheets.client.CellQuery) and
                query.min_row == 1 and
                query.max_row == 2 and
                query.min_col == 1 and
                query.max_col == 5 and
                query.return_empty == False)
    ).AndReturn(
        FakeCellsFeed([
            ('1', '1', 'honoka'),
            ('1', '2', 'eri'),
            ('1', '3', 'kotori'),
            ('1', '4', 'umi'),
            ('1', '5', 'rin'),
            ('2', '1', 'maki'),
            ('2', '2', 'nozomi'),
            ('2', '3', 'hanayo'),
            ('2', '4', 'niko'),
        ]))

  def test_read(self):
    self.set_read_expectations()

    self.mox.ReplayAll()

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
    self.client.batch(
        mox.Func(
            lambda feed:
                len(feed.entry) == 4 and
                feed.entry[0].cell.row == '2' and
                feed.entry[0].cell.col == '4' and
                feed.entry[0].cell.input_value == 'nicco' and
                feed.entry[1].cell.row == '2' and
                feed.entry[1].cell.col == '4' and
                feed.entry[1].cell.input_value == 'nicco' and
                feed.entry[2].cell.row == '2' and
                feed.entry[2].cell.col == '4' and
                feed.entry[2].cell.input_value == 'ni' and
                feed.entry[3].cell.row == '1' and
                feed.entry[3].cell.col == '3' and
                feed.entry[3].cell.input_value == 'chunchun'),
        force=True)

    self.mox.ReplayAll()

    self.worksheet.commit()  # empty commit does nothing
    self.worksheet[1][3] = 'nicco'
    self.worksheet[1][3] = 'nicco'
    self.worksheet[1][3] = 'ni'
    self.worksheet[0][-3] = 'chunchun'
    self.assertRaises(IndexError, self.worksheet[1].__setitem__, 5, '(*8*)')
    self.worksheet.commit()

  def test_write_slice(self):
    self.client.batch(
        mox.Func(
            lambda feed:
                len(feed.entry) == 9 and
                feed.entry[0].cell.row == '1' and
                feed.entry[0].cell.col == '1' and
                feed.entry[0].cell.input_value == 'honoka' and
                feed.entry[1].cell.row == '1' and
                feed.entry[1].cell.col == '2' and
                feed.entry[1].cell.input_value == 'eri' and
                feed.entry[2].cell.row == '1' and
                feed.entry[2].cell.col == '3' and
                feed.entry[2].cell.input_value == 'kotori' and
                feed.entry[3].cell.row == '1' and
                feed.entry[3].cell.col == '4' and
                feed.entry[3].cell.input_value == 'umi' and
                feed.entry[4].cell.row == '1' and
                feed.entry[4].cell.col == '5' and
                feed.entry[4].cell.input_value == 'rin' and
                feed.entry[5].cell.row == '2' and
                feed.entry[5].cell.col == '1' and
                feed.entry[5].cell.input_value == 'maki' and
                feed.entry[6].cell.row == '2' and
                feed.entry[6].cell.col == '2' and
                feed.entry[6].cell.input_value == 'nozomi' and
                feed.entry[7].cell.row == '2' and
                feed.entry[7].cell.col == '3' and
                feed.entry[7].cell.input_value == 'hanayo' and
                feed.entry[8].cell.row == '2' and
                feed.entry[8].cell.col == '4' and
                feed.entry[8].cell.input_value == 'niko'),
        force=True)

    self.mox.ReplayAll()

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
    self.client.batch(
        mox.Func(
            lambda feed:
                len(feed.entry) == 5 and
                feed.entry[0].cell.row == '1' and
                feed.entry[0].cell.col == '1' and
                feed.entry[0].cell.input_value == '28' and
                feed.entry[1].cell.row == '1' and
                feed.entry[1].cell.col == '2' and
                feed.entry[1].cell.input_value == '2.83000000000000007105e+01'
                and
                feed.entry[2].cell.row == '1' and
                feed.entry[2].cell.col == '3' and
                feed.entry[2].cell.input_value == 'kotori-chan' and
                feed.entry[3].cell.row == '1' and
                feed.entry[3].cell.col == '5' and
                feed.entry[3].cell.input_value == 'nya' and
                feed.entry[4].cell.row == '2' and
                feed.entry[4].cell.col == '5' and
                feed.entry[4].cell.input_value == ''),
        force=True)
    nya = self.mox.CreateMockAnything()
    nya.__unicode__().AndReturn(u'nya')

    self.mox.ReplayAll()

    self.worksheet.commit()  # empty commit does nothing
    self.worksheet[0][0] = 28
    self.worksheet[0][1] = 28.3
    self.worksheet[0][2] = 'kotori-chan'
    self.assertRaises(
        UnicodeDecodeError, self.worksheet[0].__setitem__, 3, '\xe6\xb5\xb7')
    self.worksheet[0][4] = nya
    self.assertRaises(IndexError, self.worksheet[0].__setitem__, 5, '(*8*)')
    self.worksheet[1][4] = None
    self.worksheet.commit()

  def test_write_with(self):
    self.client.batch(
        mox.Func(
            lambda feed:
                len(feed.entry) == 1 and
                feed.entry[0].cell.row == '2' and
                feed.entry[0].cell.col == '4'),
        force=True)

    self.mox.ReplayAll()

    with self.worksheet:
      self.worksheet[1][3] = 'nico'

  def test_nonzero(self):
    self.assertFalse(self.worksheet[0:0])
    self.assertFalse(self.worksheet[0][0:0])
    self.assertFalse(
        self.worksheet.view(start_row=0, end_row=0, start_col=0, end_col=0))

  def test_refresh(self):
    self.set_read_expectations()
    self.client.get_worksheet('cinamon', 's1').AndReturn(
        FakeWorksheetFeed('Summary', '2', '2'))
    self.client.get_cells(
        'cinamon', 's1',
        query=mox.Func(
            lambda query:
                isinstance(query, gdata.spreadsheets.client.CellQuery) and
                query.min_row == 1 and
                query.max_row == 2 and
                query.min_col == 1 and
                query.max_col == 2 and
                query.return_empty == False)
    ).AndReturn(
        FakeCellsFeed([
            ('1', '1', 'C++'), ('1', '2', 'Java'), ('2', '1', 'Python')]))

    self.mox.ReplayAll()

    self.assertEqual('Sheet1', self.worksheet.title)
    self.assertEqual(2, self.worksheet.rows)
    self.assertEqual(5, self.worksheet.cols)
    self.assertEqual(2, len(self.worksheet))
    self.assertEqual(5, len(self.worksheet[0]))

    self.assertEqual('honoka', self.worksheet[0][0])
    self.worksheet[0][0] = 'yukiho'  # this operation is discarded
    self.worksheet.refresh()

    self.assertEqual('Summary', self.worksheet.title)
    self.assertEqual(2, self.worksheet.rows)
    self.assertEqual(2, self.worksheet.cols)
    self.assertEqual(2, len(self.worksheet))
    self.assertEqual(2, len(self.worksheet[0]))

    self.assertEqual('C++', self.worksheet[0][0])

    self.worksheet.commit()  # nothing to commit

  def test_set_size(self):
    self.client.update(
        FakeWorksheetFeed('Sheet1', '7', '8'),
        uri=gdata.spreadsheets.client.WORKSHEET_URL % ('cinamon', 's1'),
        force=True)
    self.client.get_worksheet('cinamon', 's1').AndReturn(
        FakeWorksheetFeed('Sheet1', '7', '8'))

    self.mox.ReplayAll()

    self.worksheet.set_size(7, 8)
    self.assertEqual(7, self.worksheet.rows)
    self.assertEqual(8, self.worksheet.cols)
    self.assertEqual(7, len(self.worksheet))
    self.assertEqual(8, len(self.worksheet[0]))

  def test_title(self):
    self.assertEqual('Sheet1', self.worksheet.title)

  def test_title_setter(self):
    self.client.update(
        FakeWorksheetFeed('Summary', '2', '5'),
        uri=gdata.spreadsheets.client.WORKSHEET_URL % ('cinamon', 's1'),
        force=True)
    self.client.get_worksheet('cinamon', 's1').AndReturn(
        FakeWorksheetFeed('Summary', '2', '5'))

    self.mox.ReplayAll()

    self.worksheet.title = 'Summary'
    self.assertEqual('Summary', self.worksheet.title)

  def test_rows(self):
    self.assertEqual(2, self.worksheet.rows)

  def test_rows_setter(self):
    self.client.update(
        FakeWorksheetFeed('Sheet1', '7', '5'),
        uri=gdata.spreadsheets.client.WORKSHEET_URL % ('cinamon', 's1'),
        force=True)
    self.client.get_worksheet('cinamon', 's1').AndReturn(
        FakeWorksheetFeed('Sheet1', '7', '5'))

    self.mox.ReplayAll()

    self.worksheet.rows = 7
    self.assertEqual(7, self.worksheet.rows)
    self.assertEqual(5, self.worksheet.cols)

  def test_cols(self):
    self.assertEqual(5, self.worksheet.cols)

  def test_cols_setter(self):
    self.client.update(
        FakeWorksheetFeed('Sheet1', '2', '8'),
        uri=gdata.spreadsheets.client.WORKSHEET_URL % ('cinamon', 's1'),
        force=True)
    self.client.get_worksheet('cinamon', 's1').AndReturn(
        FakeWorksheetFeed('Sheet1', '2', '8'))

    self.mox.ReplayAll()

    self.worksheet.cols = 8
    self.assertEqual(2, self.worksheet.rows)
    self.assertEqual(8, self.worksheet.cols)

  def test_len(self):
    self.assertEqual(2, len(self.worksheet))
    self.assertEqual(5, len(self.worksheet[0]))

  def test_iter(self):
    self.set_read_expectations()

    self.mox.ReplayAll()

    it = iter(self.worksheet)
    self.assertEqual(['honoka', 'eri', 'kotori', 'umi', 'rin'], it.next())
    self.assertEqual(['maki', 'nozomi', 'hanayo', 'niko', ''], it.next())
    self.assertRaises(StopIteration, it.next)

  def test_repr(self):
    self.set_read_expectations()

    self.mox.ReplayAll()

    self.assertEqual(
        repr([['honoka', 'eri', 'kotori', 'umi', 'rin'],
              ['maki', 'nozomi', 'hanayo', 'niko', '']]),
        repr(self.worksheet))

  def test_view(self):
    self.client.get_cells(
        'cinamon', 's1',
        query=mox.Func(
            lambda query:
                isinstance(query, gdata.spreadsheets.client.CellQuery) and
                query.min_row == 1 and
                query.max_row == 1 and
                query.min_col == 3 and
                query.max_col == 5 and
                query.return_empty == False)
    ).AndReturn(
        FakeCellsFeed([
            ('1', '3', 'kotori'), ('1', '4', 'umi'), ('1', '5', 'rin')]))

    self.mox.ReplayAll()

    view = self.worksheet.view()
    self.assertEqual(0, view.start_row)
    self.assertEqual(2, view.end_row)
    self.assertEqual(0, view.start_col)
    self.assertEqual(5, view.end_col)
    self.assertEqual(2, view.rows)
    self.assertEqual(5, view.cols)

    self.assertRaises(IndexError, self.worksheet.view, start_row=3)
    self.assertRaises(IndexError, self.worksheet.view, end_row=-1)
    self.assertRaises(IndexError, self.worksheet.view, start_row=1, end_row=0)
    self.assertRaises(IndexError, self.worksheet.view, start_col=6)
    self.assertRaises(IndexError, self.worksheet.view, end_col=-1)
    self.assertRaises(IndexError, self.worksheet.view, start_col=1, end_col=0)

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
