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

import six

from . import py3
from . import util


class View(util.CustomMutableFixedList):

    def __init__(self, worksheet, api, start_row, end_row, start_col, end_col):
        self._worksheet = worksheet
        self._api = api
        self._start_row = start_row
        self._end_row = end_row
        self._start_col = start_col
        self._end_col = end_col
        self._view_rows = [
            ViewRow(self, row, start_col, end_col)
            for row in py3.range(start_row, end_row)]
        self._input_value_map = {}
        self._cells_fetched = False
        self._queued_updates = []

    def refresh(self):
        self._input_value_map.clear()
        self._cells_fetched = False
        del self._queued_updates[:]

    def _ensure_cells_fetched(self):
        if self._cells_fetched:
            return
        range_str = util.format_range_a1_notation(
            self._worksheet.title, self._start_row, self._end_row,
            self._start_col, self._end_col)
        response = self._api.sheets.spreadsheets().values().get(
            spreadsheetId=self._worksheet._spreadsheet.key,
            range=py3.str_to_native_str(range_str, encoding='utf-8'),
            majorDimension='ROWS',
            valueRenderOption='FORMATTED_VALUE',
            dateTimeRenderOption='FORMATTED_STRING').execute()
        self._input_value_map = {}
        for i, row in enumerate(response.get('values', [])):
            index_row = self._start_row + i
            for j, value in enumerate(row):
                index_col = self._start_col + j
                self._input_value_map.setdefault((index_row, index_col), value)
        self._cells_fetched = True

    def commit(self):
        if not self._queued_updates:
            return
        request = {
            'data': [
                {
                    'range': util.format_range_a1_notation(
                        self._worksheet.title, row, row + 1, col, col + 1),
                    'majorDimension': 'ROWS',
                    'values': [[value]],
                }
                for row, col, value in self._queued_updates
            ],
            'valueInputOption': 'USER_ENTERED',
            'includeValuesInResponse': False,
        }
        self._api.sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=self._worksheet._spreadsheet.key,
            body=request).execute()
        del self._queued_updates[:]

    def __getitem__(self, index):
        return self._view_rows[index]

    def __setitem__(self, index, new_value):
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            if step != 1:
                raise NotImplementedError('slicing with step is not supported')
            if stop < start:
                stop = start
            if len(new_value) != stop - start:
                raise ValueError(
                    'Tried to assign %d values to %d element slice' %
                    (len(new_value), stop - start))
            for i, new_value_one in py3.zip(py3.range(start, stop), new_value):
                self[i] = new_value_one
            return
        self._view_rows[index][:] = new_value

    def __len__(self):
        return self.rows

    def __iter__(self):
        return iter(self._view_rows)

    def __repr__(self):
        return str('View(%r)') % (self._view_rows,)

    @property
    def rows(self):
        return self._end_row - self._start_row

    @property
    def cols(self):
        return self._end_col - self._start_col

    @property
    def start_row(self):
        return self._start_row

    @property
    def end_row(self):
        return self._end_row

    @property
    def start_col(self):
        return self._start_col

    @property
    def end_col(self):
        return self._end_col


class ViewRow(util.CustomMutableFixedList):

    def __init__(self, view, row, start_col, end_col):
        self._view = view
        self._row = row
        self._start_col = start_col
        self._end_col = end_col

    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            if step != 1:
                raise NotImplementedError('slicing with step is not supported')
            if stop < start:
                stop = start
            return ViewRow(
                self._view, self._row,
                self._start_col + start, self._start_col + stop)
        util.check_type(index, six.integer_types)
        if index < 0:
            col = self._end_col + index
        else:
            col = self._start_col + index
        if not (self._start_col <= col < self._end_col):
            raise IndexError('Column %d is out of range.' % col)
        if (self._row, col) not in self._view._input_value_map:
            self._view._ensure_cells_fetched()
        return self._view._input_value_map.get((self._row, col), '')

    def __setitem__(self, index, new_value):
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            if step != 1:
                raise NotImplementedError('slicing with step is not supported')
            if stop < start:
                stop = start
            if len(new_value) != stop - start:
                raise ValueError(
                    'Tried to assign %d values to %d element slice' %
                    (len(new_value), stop - start))
            for i, new_value_one in py3.zip(py3.range(start, stop), new_value):
                self[i] = new_value_one
            return
        util.check_type(index, six.integer_types)
        if index < 0:
            col = self._end_col + index
        else:
            col = self._start_col + index
        if not (self._start_col <= col < self._end_col):
            raise IndexError('Column %d is out of range.' % col)
        if new_value is None:
            new_value = ''
        elif isinstance(new_value, six.integer_types):
            new_value = '%d' % new_value
        elif isinstance(new_value, float):
            # Do best not to lose precision...
            new_value = '%.20e' % new_value
        elif isinstance(new_value, py3.bytes):
            # May raise UnicodeDecodeError.
            new_value = new_value.decode('ascii')
        elif not isinstance(new_value, py3.str):
            new_value = py3.str(new_value)
        assert isinstance(new_value, py3.str)
        self._view._input_value_map[(self._row, col)] = new_value
        self._view._queued_updates.append((self._row, col, new_value))

    def __len__(self):
        return self._end_col - self._start_col

    def __iter__(self):
        self._view._ensure_cells_fetched()
        for col in py3.range(self._start_col, self._end_col):
            yield self._view._input_value_map.get((self._row, col), '')

    def __repr__(self):
        return repr(list(self))
