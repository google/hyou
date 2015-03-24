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
import json

import gdata.gauth
import gdata.spreadsheets.client
import gdata.spreadsheets.data
import oauth2client.client

from . import util


GOOGLE_SPREADSHEET_SCOPES = (
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
)


class Collection(util.LazyOrderedDictionary):
  def __init__(self, credentials):
    super(Collection, self).__init__(
        self._spreadsheet_enumerator,
        self._spreadsheet_constructor)
    self.credentials = credentials
    self.auth_token = gdata.gauth.OAuth2TokenFromCredentials(self.credentials)
    # Don't use auth_token= argument. It does not refresh tokens.
    self.client = gdata.spreadsheets.client.SpreadsheetsClient()
    self.auth_token.authorize(self.client)

  @classmethod
  def login(cls, json_path=None, json_data=None):
    if (json_path is None) == (json_data is None):
      raise TypeError('login() requires either json_path or json_data')
    if json_data is None:
      with open(json_path, 'rb') as f:
        json_data = f.read()
    credentials = oauth2client.client.OAuth2Credentials.from_json(json_data)
    return cls(credentials)

  @classmethod
  def login_as_service_account(
      cls,
      service_account_name,
      private_key_path=None,
      private_key_data=None,
      private_key_password='notasecret'):
    if (private_key_path is None) == (private_key_data is None):
      raise TypeError(
          'login_as_service_account() requires either private_key_path or '
          'private_key_data')
    if private_key_data is None:
      with open(private_key_path, 'rb') as f:
        private_key_data = f.read()
    credentials = oauth2client.client.SignedJwtAssertionCredentials(
        service_account_name=service_account_name,
        private_key=private_key_data,
        private_key_password=private_key_password,
        scope=GOOGLE_SPREADSHEET_SCOPES)
    return cls(credentials)

  def refresh(self):
    super(Collection, self).refresh()

  def _spreadsheet_enumerator(self):
    feed = self.client.get_spreadsheets()
    for entry in feed.entry:
      key = entry.get_spreadsheet_key()
      yield (key, Spreadsheet(self, self.client, key, entry))

  def _spreadsheet_constructor(self, key):
    # TODO: Upstream to gdata.
    entry = self.client.get_feed(
        'https://spreadsheets.google.com/feeds/spreadsheets/private/full/%s' %
        key,
        desired_class=gdata.spreadsheets.data.Spreadsheet)
    key = entry.get_spreadsheet_key()
    return Spreadsheet(self, self.client, key, entry)


class Spreadsheet(util.LazyOrderedDictionary):
  def __init__(self, collection, client, key, entry):
    super(Spreadsheet, self).__init__(self._worksheet_enumerator, None)
    self.collection = collection
    self.client = client
    self.key = key
    self._entry = entry

  def refresh(self):
    super(Spreadsheet, self).refresh()
    # TODO: Upstream to gdata.
    self._entry = self.client.get_feed(
        'https://spreadsheets.google.com/feeds/spreadsheets/private/full/%s' %
        self.key,
        desired_class=gdata.spreadsheets.data.Spreadsheet)

  @property
  def title(self):
    return self._entry.title.text

  @property
  def updated(self):
    return datetime.datetime.strptime(
        self._entry.updated.text, '%Y-%m-%dT%H:%M:%S.%fZ')

  def _worksheet_enumerator(self):
    feed = self.client.get_worksheets(self.key)
    for entry in feed.entry:
      key = entry.get_worksheet_id()
      worksheet = Worksheet(self, self.client, key, entry)
      yield (worksheet.name, worksheet)


class WorksheetView(object):
  def __init__(self, worksheet, client, start_row, end_row, start_col, end_col):
    self.worksheet = worksheet
    self.client = client
    self.start_row = start_row
    self.end_row = end_row
    self.start_col = start_col
    self.end_col = end_col
    self._view_rows = [
        WorksheetViewRow(self, row, start_col, end_col)
        for row in xrange(start_row, end_row)]
    self._input_value_map = {}
    self._cells_fetched = False
    self._queued_updates = []
    self.refresh()

  def refresh(self):
    self._input_value_map.clear()
    self._cells_fetched = False
    del self._queued_updates[:]

  def _ensure_cells_fetched(self):
    if self._cells_fetched:
      return
    query = gdata.spreadsheets.client.CellQuery(
        min_row=(self.start_row + 1),
        max_row=self.end_row,
        min_col=(self.start_col + 1),
        max_col=self.end_col,
        return_empty=False)
    feed = self.client.get_cells(self.worksheet.spreadsheet.key, self.worksheet.key, query=query)
    self._input_value_map = {}
    for entry in feed.entry:
      cell = entry.cell
      self._input_value_map.setdefault((int(cell.row) - 1, int(cell.col) - 1), cell.input_value)
    self._cells_fetched = True

  def commit(self):
    feed = gdata.spreadsheets.data.build_batch_cells_update(self.worksheet.spreadsheet.key, self.worksheet.key)
    for row, col, new_value in self._queued_updates:
      feed.add_set_cell(row + 1, col + 1, new_value)
    self.client.batch(feed, force=True)
    del self._queued_updates[:]

  def __getitem__(self, index):
    return self._view_rows[index]

  def __len__(self):
    return self.rows

  def __iter__(self):
    for row in self._view_rows:
      yield row

  def __repr__(self):
    return '<%s %r>' % (self.__class__.__name__, self._view_rows,)

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

  def __getitem__(self, index):
    if isinstance(index, slice):
      start, stop, step = index.indices(len(self))
      assert step == 1, 'slicing with step is not supported'
      if stop < start:
        stop = start
      return WorksheetViewRow(
          self._view, self._row,
          self._start_col + start, self._end_col + stop)
    assert isinstance(index, int)
    col = self._start_col + index
    if not (self._start_col <= col < self._end_col):
      raise KeyError()
    if (self._row, col) not in self._view._input_value_map:
      self._view._ensure_cells_fetched()
    return self._view._input_value_map.get((self._row, col))

  def __setitem__(self, index, new_value):
    assert isinstance(index, int)
    col = self._start_col + index
    if not (self._start_col <= col < self._end_col):
      raise KeyError()
    if new_value is None:
      pass
    elif isinstance(new_value, int):
      new_value = u'%d' % new_value
    elif isinstance(new_value, float):
      # Do best not to lose precision...
      new_value = u'%20e' % new_value
    elif isinstance(new_value, str):
      new_value = new_value.encode('utf-8')
    elif not isinstance(new_value, unicode):
      new_value = unicode(new_value)
    self._view._input_value_map[(self._row, col)] = new_value
    self._view._queued_updates.append((self._row, col, new_value))

  def __len__(self):
    return self._end_col - self._start_col

  def __iter__(self):
    self._view._ensure_cells_fetched()
    for col in xrange(self._start_col, self._end_col):
      yield self._view._input_value_map.get((self._row, col))

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
      raise KeyError()
    if not (0 <= start_col <= end_col <= self.cols):
      raise KeyError()
    return WorksheetView(
        self, self.client,
        start_row=start_row, end_row=end_row,
        start_col=start_col, end_col=end_col)

  @property
  def name(self):
    return self._entry.title.text

  @property
  def rows(self):
    return int(self._entry.row_count.text)

  @property
  def cols(self):
    return int(self._entry.col_count.text)
