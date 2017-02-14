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

import httplib2

from . import api
from . import py3
from . import spreadsheet
from . import util


class Collection(util.LazyOrderedDictionary):

    def __init__(self, api):
        super(Collection, self).__init__(
            self._spreadsheet_enumerator,
            self._spreadsheet_constructor)
        self._api = api

    @classmethod
    def login(cls, json_path=None, json_text=None, discovery=False):
        if json_text is None:
            with py3.open(json_path, 'r') as f:
                json_text = f.read()
        credentials = util.parse_credentials(json_text)
        http = credentials.authorize(httplib2.Http())
        return cls(api.API(http, discovery=discovery))

    def create_spreadsheet(self, title, rows=1000, cols=26):
        body = {
            'title': title,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
        }
        response = self._api.drive.files().insert(body=body).execute()
        key = response['id']
        self.refresh()
        spreadsheet = self[key]
        spreadsheet[0].set_size(rows, cols)
        return spreadsheet

    def _spreadsheet_enumerator(self):
        response = self._api.drive.files().list(
            maxResults=1000,
            q=('mimeType="application/vnd.google-apps.spreadsheet" and '
               'trashed = false'),
            fields='items/id').execute()
        for item in response['items']:
            key = item['id']
            yield (key, spreadsheet.Spreadsheet(self._api, key, None))

    def _spreadsheet_constructor(self, key):
        entry = self._api.sheets.spreadsheets().get(
            spreadsheetId=key, includeGridData=False).execute()
        return spreadsheet.Spreadsheet(
            self._api, entry['spreadsheetId'], entry)
