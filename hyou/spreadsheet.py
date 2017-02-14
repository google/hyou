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

import datetime

from . import util
from . import worksheet


class Spreadsheet(util.LazyOrderedDictionary):

    def __init__(self, api, key, entry):
        super(Spreadsheet, self).__init__(self._worksheet_enumerator, None)
        self._api = api
        self._key = str(key)
        self._entry = entry
        self._updated = None

    def __repr__(self):
        return str('Spreadsheet(key=%r)') % (self.key,)

    def refresh(self, entry=None):
        if entry is not None:
            self._entry = entry
        else:
            self._entry = self._api.sheets.spreadsheets().get(
                spreadsheetId=self.key, includeGridData=False).execute()
        self._updated = None
        super(Spreadsheet, self).refresh()

    def add_worksheet(self, title, rows=1000, cols=26):
        new_entry = self._make_single_batch_request(
            'addSheet',
            {
                'properties': {
                    'title': title,
                    'gridProperties': {
                        'rowCount': rows,
                        'columnCount': cols,
                    },
                },
            })
        self.refresh(new_entry)
        return self[title]

    def delete_worksheet(self, title):
        worksheet = self[title]
        new_entry = self._make_single_batch_request(
            'deleteSheet',
            {'sheetId': worksheet.key})
        self.refresh(new_entry)

    @property
    def key(self):
        return self._key

    @property
    def url(self):
        return 'https://docs.google.com/spreadsheets/d/%s/edit' % self.key

    @property
    def title(self):
        self._ensure_entry()
        return self._entry['properties']['title']

    @title.setter
    def title(self, new_title):
        new_entry = self._make_single_batch_request(
            'updateSpreadsheetProperties',
            {
                'properties': {
                    'title': new_title,
                },
                'fields': 'title',
            })
        self.refresh(new_entry)

    @property
    def updated(self):
        if not self._updated:
            response = self._api.drive.files().get(fileId=self.key).execute()
            self._updated = datetime.datetime.strptime(
                response['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
        return self._updated

    def _ensure_entry(self):
        if self._entry is None:
            self.refresh()

    def _worksheet_enumerator(self):
        self._ensure_entry()
        for sheet_entry in self._entry['sheets']:
            aworksheet = worksheet.Worksheet(self, self._api, sheet_entry)
            yield (aworksheet.title, aworksheet)

    def _make_single_batch_request(self, method, params):
        request = {
            'requests': [{method: params}],
            'include_spreadsheet_in_response': True,
        }
        response = self._api.sheets.spreadsheets().batchUpdate(
            spreadsheetId=self.key, body=request).execute()
        return response['updatedSpreadsheet']
