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

"""Performs OAuth2 Web Server Flow to obtain credentials.

Usage:
generate_oauth2_credentials.py [--client_id=CLIENT_ID --client_secret=CLIENT_SECRET] OUTPUT_JSON_PATH
"""

import os
import sys

import gflags
import hyou.client
import oauth2client.client

FLAGS = gflags.FLAGS

TEST_CLIENT_ID = '958069810280-th697if59r9scrf1qh0sg6gd9d9u0kts.apps.googleusercontent.com'
TEST_CLIENT_SECRET = '5nlcvd54WycOd8h8w7HD0avT'

gflags.DEFINE_string('client_id', TEST_CLIENT_ID, '')
gflags.DEFINE_string('client_secret', TEST_CLIENT_SECRET, '')
gflags.MarkFlagAsRequired('client_id')
gflags.MarkFlagAsRequired('client_secret')


def main(argv):
  if len(argv) != 2:
    print 'usage: generate_oauth2_credentials.py OUTPUT_JSON_PATH'
    return 1
  output_json_path = argv[1]

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

  with open(output_json_path, 'w') as f:
    os.fchmod(f.fileno(), 0600)
    f.write(credentials.to_json())

  print
  print 'Credentials successfully saved to %s' % output_json_path
  print
  print 'WARNING: Keep it in a safe location! With the credentials, all your Google Drive documents can be accessed.'


if __name__ == '__main__':
  sys.exit(main(FLAGS(sys.argv)))
