#!/usr/bin/python
#
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

"""Uploads a sheet file (CSV/TSV) to Google Spreadsheet.

Usage:
upload_sheet.py --authenticate
upload_sheet.py <filename>
"""

import csv
import os
import sys

import gflags
import hyou
import hyou.client
import oauth2client.client

CREDENTIAL_PATH = os.path.join(os.environ['HOME'], '.hyou.credential.json')
TEST_CLIENT_ID = '958069810280-th697if59r9scrf1qh0sg6gd9d9u0kts.apps.googleusercontent.com'
TEST_CLIENT_SECRET = '5nlcvd54WycOd8h8w7HD0avT'

FLAGS = gflags.FLAGS

gflags.DEFINE_bool('authenticate', False, '')
gflags.DEFINE_string('client_id', TEST_CLIENT_ID, '')
gflags.DEFINE_string('client_secret', TEST_CLIENT_SECRET, '')
gflags.MarkFlagAsRequired('client_id')
gflags.MarkFlagAsRequired('client_secret')


def load_sheet(path):
  with open(path, 'rb') as f:
    reader = csv.reader(f)
    return list(reader)


def upload_main(argv):
  if len(argv) != 2:
    return __doc__

  path = argv[1]

  sheet = load_sheet(path)

  try:
    collection = hyou.login(json_path=CREDENTIAL_PATH)
  except Exception:
    return ('Your credential is missing, expired or invalid.'
            'Please authenticate again by --authenticate.')

  title = os.path.basename(path).decode('utf-8')
  spreadsheet = collection.create_spreadsheet(
      title, rows=len(sheet), cols=len(sheet[0]))

  with spreadsheet[0] as worksheet:
    for srow, trow in zip(sheet, worksheet):
      for i, value in enumerate(srow):
        trow[i] = value.decode('utf-8')

  print spreadsheet.url


def authenticate_main(argv):
  flow = oauth2client.client.OAuth2WebServerFlow(
      client_id=FLAGS.client_id,
      client_secret=FLAGS.client_secret,
      scope=hyou.client.GOOGLE_SPREADSHEET_SCOPES)
  url = flow.step1_get_authorize_url('urn:ietf:wg:oauth:2.0:oob')

  print
  print 'Please visit this URL to get the authorization code:'
  print url
  print

  code = raw_input('Code: ').strip()

  credentials = flow.step2_exchange(code)

  with open(CREDENTIAL_PATH, 'w') as f:
    os.fchmod(f.fileno(), 0600)
    f.write(credentials.to_json())

  print
  print 'OK! Credentials were saved at %s' % CREDENTIAL_PATH


def main(argv):
  if FLAGS.authenticate:
    return authenticate_main(argv)
  else:
    return upload_main(argv)


if __name__ == '__main__':
  sys.exit(main(FLAGS(sys.argv)))
