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

import collections
import datetime
import itertools
import json

import apiclient.discovery
import apiclient.http
import gdata.gauth
import gdata.spreadsheets.client
import gdata.spreadsheets.data
import httplib2
import oauth2client.client
import oauth2client.service_account

from . import util


GOOGLE_SPREADSHEET_SCOPES = (
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
)

SPREADSHEET_URL = (
    'https://spreadsheets.google.com/feeds/spreadsheets/private/full/%s')


class Collection(util.LazyOrderedDictionary):
  def __init__(self, client, drive):
    super(Collection, self).__init__(
        self._spreadsheet_enumerator,
        self._spreadsheet_constructor)
    self.client = client
    self.drive = drive

  @classmethod
  def login(cls, json_path=None, json_text=None):
    if json_text is None:
      with open(json_path, 'r') as f:
        json_text = f.read()
    json_data = json.loads(json_text)
    if '_module' in json_data:
      credentials = oauth2client.client.Credentials.new_from_json(json_text)
    elif 'private_key' in json_data:
      credentials = (
          oauth2client.service_account.ServiceAccountCredentials
          .from_json_keyfile_dict(
              json_data,
              scopes=GOOGLE_SPREADSHEET_SCOPES))
    else:
      raise ValueError('unrecognized credential format')
    # Don't use auth_token= argument. It does not refresh tokens.
    client = gdata.spreadsheets.client.SpreadsheetsClient()
    auth_http = httplib2.Http()
    auth_token = gdata.gauth.OAuth2TokenFromCredentials(credentials)
    auth_token.authorize(client)
    auth_http = credentials.authorize(auth_http)
    drive = apiclient.discovery.build('drive', 'v2', http=auth_http)
    return cls(client, drive)

  def create_spreadsheet(self, title, rows=1000, cols=26):
    body = {
        'title': title,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
    }
    response = self.drive.files().insert(body=body).execute()
    key = response['id']
    self.refresh()
    spreadsheet = self[key]
    if (rows, cols) != (1000, 26):
      spreadsheet[0].set_size(rows, cols)
    return spreadsheet

  def _spreadsheet_enumerator(self):
    feed = self.client.get_spreadsheets()
    for entry in feed.entry:
      key = entry.get_spreadsheet_key()
      yield (key, Spreadsheet(self, self.client, self.drive, key, entry))

  def _spreadsheet_constructor(self, key):
    # TODO: Upstream to gdata.
    entry = self.client.get_feed(
        SPREADSHEET_URL % key,
        desired_class=gdata.spreadsheets.data.Spreadsheet)
    key = entry.get_spreadsheet_key()
    return Spreadsheet(self, self.client, self.drive, key, entry)


class Spreadsheet(util.LazyOrderedDictionary):
  def __init__(self, collection, client, drive, key, entry):
    super(Spreadsheet, self).__init__(self._worksheet_enumerator, None)
    self.collection = collection
    self.client = client
    self.drive = drive
    self.key = key
    self._entry = entry

  def refresh(self):
    super(Spreadsheet, self).refresh()
    # TODO: Upstream to gdata.
    self._entry = self.client.get_feed(
        SPREADSHEET_URL % self.key,
        desired_class=gdata.spreadsheets.data.Spreadsheet)

  def add_worksheet(self, title, rows=1000, cols=26):
    self.client.add_worksheet(self.key, title, rows=rows, cols=cols)
    self.refresh()
    return self[title]

  def delete_worksheet(self, title):
    worksheet = self[title]
    url = gdata.spreadsheets.client.WORKSHEET_URL % (self.key, worksheet.key)
    self.client.delete(url, force=True)
    self.refresh()

  @property
  def url(self):
    return 'https://docs.google.com/spreadsheets/d/%s/edit' % self.key

  @property
  def title(self):
    return self._entry.title.text

  @title.setter
  def title(self, new_title):
    body = {'title': new_title}
    response = self.drive.files().update(fileId=self.key, body=body).execute()
    self.refresh()

  @property
  def updated(self):
    return datetime.datetime.strptime(
        self._entry.updated.text, '%Y-%m-%dT%H:%M:%S.%fZ')

  def _worksheet_enumerator(self):
    feed = self.client.get_worksheets(self.key)
    for entry in feed.entry:
      key = entry.get_worksheet_id()
      worksheet = Worksheet(self, self.client, key, entry)
      yield (worksheet.title, worksheet)


class WorksheetView(object):
  def __init__(self, worksheet, client, start_row, end_row, start_col, end_col):
    self.worksheet = worksheet
    self.client = client
    self._reset_size(start_row, end_row, start_col, end_col)
    self._input_value_map = {}
    self._cells_fetched = False
    self._queued_updates = []

  def refresh(self):
    self._input_value_map.clear()
    self._cells_fetched = False
    del self._queued_updates[:]

  def _reset_size(self, start_row, end_row, start_col, end_col):
    self.start_row = start_row
    self.end_row = end_row
    self.start_col = start_col
    self.end_col = end_col
    self._view_rows = [
        WorksheetViewRow(self, row, start_col, end_col)
        for row in xrange(start_row, end_row)]

  def _ensure_cells_fetched(self):
    if self._cells_fetched:
      return
    query = gdata.spreadsheets.client.CellQuery(
        min_row=(self.start_row + 1),
        max_row=self.end_row,
        min_col=(self.start_col + 1),
        max_col=self.end_col,
        return_empty=False)
    feed = self.client.get_cells(
        self.worksheet.spreadsheet.key, self.worksheet.key, query=query)
    self._input_value_map = {}
    for entry in feed.entry:
      cell = entry.cell
      self._input_value_map.setdefault(
          (int(cell.row) - 1, int(cell.col) - 1),
          cell.input_value)
    self._cells_fetched = True

  def commit(self):
    if not self._queued_updates:
      return
    feed = gdata.spreadsheets.data.build_batch_cells_update(
        self.worksheet.spreadsheet.key, self.worksheet.key)
    for row, col, new_value in self._queued_updates:
      feed.add_set_cell(row + 1, col + 1, new_value)
    self.client.batch(feed, force=True)
    del self._queued_updates[:]

  def __nonzero__(self):
    return len(self) > 0

  def __getitem__(self, index):
    return self._view_rows[index]

  def __len__(self):
    return self.rows

  def __iter__(self):
    for row in self._view_rows:
      yield row

  def __repr__(self):
    return repr(self._view_rows)

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.commit()

  @property
  def rows(self):
    return self.end_row - self.start_row

  @property
  def cols(self):
    return self.end_col - self.start_col


class WorksheetViewRow(util.CustomMutableFixedList):
  def __init__(self, view, row, start_col, end_col):
    self._view = view
    self._row = row
    self._start_col = start_col
    self._end_col = end_col

  def __nonzero__(self):
    return len(self) > 0

  def __getitem__(self, index):
    if isinstance(index, slice):
      start, stop, step = index.indices(len(self))
      assert step == 1, 'slicing with step is not supported'
      if stop < start:
        stop = start
      return WorksheetViewRow(
          self._view, self._row,
          self._start_col + start, self._start_col + stop)
    assert isinstance(index, int)
    if index < 0:
      col = self._end_col + index
    else:
      col = self._start_col + index
    if not (self._start_col <= col < self._end_col):
      raise IndexError()
    if (self._row, col) not in self._view._input_value_map:
      self._view._ensure_cells_fetched()
    return self._view._input_value_map.get((self._row, col), '')

  def __setitem__(self, index, new_value):
    if isinstance(index, slice):
      start, stop, step = index.indices(len(self))
      assert step == 1, 'slicing with step is not supported'
      if stop < start:
        stop = start
      if len(new_value) != stop - start:
        raise ValueError(
            'Tried to assign %d values to %d element slice' %
            (len(new_value), stop - start))
      for i, new_value_one in itertools.izip(xrange(start, stop), new_value):
        self[i] = new_value_one
      return
    assert isinstance(index, int)
    if index < 0:
      col = self._end_col + index
    else:
      col = self._start_col + index
    if not (self._start_col <= col < self._end_col):
      raise IndexError()
    if new_value is None:
      new_value = ''
    elif isinstance(new_value, int):
      new_value = '%d' % new_value
    elif isinstance(new_value, float):
      # Do best not to lose precision...
      new_value = '%.20e' % new_value
    elif isinstance(new_value, str):
      # May raise UnicodeDecodeError.
      new_value.decode('ascii')
    elif not isinstance(new_value, unicode):
      new_value = unicode(new_value)
    self._view._input_value_map[(self._row, col)] = new_value
    self._view._queued_updates.append((self._row, col, new_value))

  def __len__(self):
    return self._end_col - self._start_col

  def __iter__(self):
    self._view._ensure_cells_fetched()
    for col in xrange(self._start_col, self._end_col):
      yield self._view._input_value_map.get((self._row, col), '')

  def __repr__(self):
    return repr([self[i] for i in xrange(len(self))])


class Worksheet(WorksheetView):
  def __init__(self, spreadsheet, client, key, entry):
    self.spreadsheet = spreadsheet
    self.client = client
    self.key = key
    self._entry = entry
    super(Worksheet, self).__init__(self, client, 0, self.rows, 0, self.cols)

  def refresh(self):
    self._entry = self.client.get_worksheet(self.spreadsheet.key, self.key)
    self._reset_size(0, self.rows, 0, self.cols)
    super(Worksheet, self).refresh()

  def view(self, start_row=None, end_row=None, start_col=None, end_col=None):
    if start_row is None:
      start_row = 0
    if end_row is None:
      end_row = self.rows
    if start_col is None:
      start_col = 0
    if end_col is None:
      end_col = self.cols
    if not (0 <= start_row <= end_row <= self.rows):
      raise IndexError()
    if not (0 <= start_col <= end_col <= self.cols):
      raise IndexError()
    return WorksheetView(
        self, self.client,
        start_row=start_row, end_row=end_row,
        start_col=start_col, end_col=end_col)

  def set_size(self, rows, cols):
    assert isinstance(rows, int) and rows > 0
    assert isinstance(cols, int) and cols > 0
    self._entry.row_count.text = str(rows)
    self._entry.col_count.text = str(cols)
    self._update()

  @property
  def title(self):
    return self._entry.title.text

  @title.setter
  def title(self, new_title):
    self._entry.title.text = new_title
    self._update()

  @property
  def rows(self):
    return int(self._entry.row_count.text)

  @rows.setter
  def rows(self, rows):
    assert isinstance(rows, int) and rows > 0
    self._entry.row_count.text = str(rows)
    self._update()

  @property
  def cols(self):
    return int(self._entry.col_count.text)

  @cols.setter
  def cols(self, cols):
    assert isinstance(cols, int) and cols > 0
    self._entry.col_count.text = str(cols)
    self._update()

  def _update(self):
    url = gdata.spreadsheets.client.WORKSHEET_URL % (
        self.spreadsheet.key, self.key)
    # TODO: Use returned entry to speed up
    unused_entry = self.client.update(self._entry, uri=url, force=True)
    self.refresh()
