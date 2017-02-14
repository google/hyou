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

import googleapiclient.discovery

from . import schema


SHEETS_API_DISCOVERY_URL = (
    'https://sheets.googleapis.com/$discovery/rest?version=v4')


class API(object):

    def __init__(self, http, discovery):
        if discovery:
            self.sheets = googleapiclient.discovery.build(
                'sheets', 'v4', http=http,
                discoveryServiceUrl=SHEETS_API_DISCOVERY_URL)
            self.drive = googleapiclient.discovery.build(
                'drive', 'v2', http=http)
        else:
            self.sheets = googleapiclient.discovery.build_from_document(
                schema.SHEETS_V4, http=http)
            self.drive = googleapiclient.discovery.build_from_document(
                schema.DRIVE_V2, http=http)
