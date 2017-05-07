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

from . import exception
from . import util
from . import view


class Worksheet(object):

    def __init__(self, spreadsheet, api, entry):
        self._spreadsheet = spreadsheet
        self._api = api
        self._entry = entry

    def __repr__(self):
        return str('Worksheet(key=%r)') % (self.key,)

    def refresh(self, entry=None):
        if entry is not None:
            self._entry = entry
        else:
            spreadsheet_entry = self._api.sheets.spreadsheets().get(
                spreadsheetId=self._spreadsheet.key,
                includeGridData=False).execute()
            for entry in spreadsheet_entry['sheets']:
                if entry['properties']['sheetId'] == self.key:
                    self._entry = entry
                    break
            else:
                raise exception.HyouRuntimeError('The sheet has been removed.')

    def view(self, start_row=None, end_row=None, start_col=None, end_col=None):
        start_row, end_row, _ = slice(start_row, end_row).indices(self.rows)
        start_col, end_col, _ = slice(start_col, end_col).indices(self.cols)
        if start_row > end_row:
            start_row = end_row
        if start_col > end_col:
            start_col = end_col
        return view.View(
            self, self._api,
            start_row=start_row, end_row=end_row,
            start_col=start_col, end_col=end_col)

    def set_size(self, rows, cols):
        util.check_type(rows, six.integer_types)
        util.check_type(cols, six.integer_types)
        if not (rows >= 0 and cols >= 0):
            raise ValueError('Non-positive size is not allowed')
        new_entry = self._make_single_batch_request(
            'updateSheetProperties',
            {
                'properties': {
                    'sheetId': self.key,
                    'gridProperties': {
                        'rowCount': rows,
                        'columnCount': cols,
                    },
                },
                'fields': 'gridProperties(rowCount,columnCount)',
            })
        self.refresh(new_entry)

    def set_frozen_size(self, rows, cols):
        util.check_type(rows, six.integer_types)
        util.check_type(cols, six.integer_types)
        if not (rows >= 0 and cols >= 0):
            raise ValueError('Non-positive size is not allowed')
        new_entry = self._make_single_batch_request(
            'updateSheetProperties',
            {
                'properties': {
                    'sheetId': self.key,
                    'gridProperties': {
                        'frozenRowCount': rows,
                        'frozenColumnCount': cols,
                    },
                },
                'fields': 'gridProperties(frozenRowCount,frozenColumnCount)',
            })
        self.refresh(new_entry)

    @property
    def key(self):
        return self._entry['properties']['sheetId']

    @property
    def title(self):
        return self._entry['properties']['title']

    @title.setter
    def title(self, new_title):
        new_entry = self._make_single_batch_request(
            'updateSheetProperties',
            {
                'properties': {
                    'sheetId': self.key,
                    'title': new_title,
                },
                'fields': 'title',
            })
        self.refresh(new_entry)

    @property
    def rows(self):
        return self._entry['properties']['gridProperties']['rowCount']

    @rows.setter
    def rows(self, rows):
        self.set_size(rows, self.cols)

    @property
    def cols(self):
        return self._entry['properties']['gridProperties']['columnCount']

    @cols.setter
    def cols(self, cols):
        self.set_size(self.rows, cols)

    @property
    def frozen_rows(self):
        return (
            self._entry['properties']['gridProperties']
            .get('frozenRowCount', 0))

    @frozen_rows.setter
    def frozen_rows(self, rows):
        self.set_frozen_size(rows, self.frozen_cols)

    @property
    def frozen_cols(self):
        return (
            self._entry['properties']['gridProperties']
            .get('frozenColumnCount', 0))

    @frozen_cols.setter
    def frozen_cols(self, cols):
        self.set_frozen_size(self.frozen_rows, cols)

    def _make_single_batch_request(self, method, params):
        spreadsheet_entry = self._spreadsheet._make_single_batch_request(
            method, params)
        for entry in spreadsheet_entry['sheets']:
            if entry['properties']['sheetId'] == self.key:
                return entry
        raise exception.HyouRuntimeError('The sheet has been removed.')
