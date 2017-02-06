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

"""Performs OAuth2 Web Server Flow to obtain credentials."""

from __future__ import (
    absolute_import, division, print_function, unicode_literals)
from builtins import (  # noqa: F401
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next,
    object, oct, open, pow, range, round, str, super, zip)

import argparse
import os
import sys

import future.utils
import hyou
import oauth2client.client

TEST_CLIENT_ID = (
    '958069810280-th697if59r9scrf1qh0sg6gd9d9u0kts.'
    'apps.googleusercontent.com')
TEST_CLIENT_SECRET = '5nlcvd54WycOd8h8w7HD0avT'


def create_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--client-id', type=str, default=TEST_CLIENT_ID,
        help='OAuth2 client ID.')
    parser.add_argument(
        '--client-secret', type=str, default=TEST_CLIENT_SECRET,
        help='OAuth2 client secret.')
    parser.add_argument(
        'output_json_path', type=str,
        help='Output JSON path.')
    return parser


def main(argv):
    parser = create_parser()
    opts = parser.parse_args(argv[1:])

    flow = oauth2client.client.OAuth2WebServerFlow(
        client_id=opts.client_id,
        client_secret=opts.client_secret,
        scope=hyou.SCOPES)
    url = flow.step1_get_authorize_url('urn:ietf:wg:oauth:2.0:oob')

    print()
    print('Please visit this URL to get the authorization code:')
    print(url)
    print()

    code = input('Code: ').strip()

    credentials = flow.step2_exchange(code)

    with open(opts.output_json_path, 'wb') as f:
        os.fchmod(f.fileno(), 0o600)
        f.write(future.utils.native_str_to_bytes(credentials.to_json()))

    print()
    print('Credentials successfully saved to %s' % opts.output_json_path)
    print()
    print('WARNING: Keep it in a safe location! With the credentials,')
    print('         all your Google Drive documents can be accessed.')


if __name__ == '__main__':
    sys.exit(main(sys.argv))
