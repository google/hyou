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

import argparse
import random
import sys

import hyou
from hyou import py3

TEST_SPREADSHEET_KEY = '1hxNAHH-DUWgFcC603mFARGYOeKUwiRq56VsHOJSA5Z0'


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--credentials', type=py3.str,
        help='Credentials JSON path.')
    return parser


def get_credentials(json_path=None):
    assert json_path  # TODO: Read from os.environ
    with py3.open(json_path, 'r') as f:
        return f.read()


def main():
    parser = create_parser()
    opts = parser.parse_args()

    collection = hyou.login(json_text=get_credentials(opts.credentials))

    spreadsheet = collection[TEST_SPREADSHEET_KEY]

    print(
        'Running tests with https://docs.google.com/spreadsheets/d/%s/edit ...'
        % TEST_SPREADSHEET_KEY)

    worksheet_title = 'sheet%08d' % random.randrange(100000000)
    worksheet = spreadsheet.add_worksheet(worksheet_title, rows=20, cols=10)

    print('Created %s' % worksheet_title)

    try:
        print('Testing...')

        assert worksheet.title == worksheet_title
        assert worksheet.rows == 20
        assert worksheet.cols == 10

        worksheet.rows = 15

        assert worksheet.rows == 15

        view = worksheet.view(start_row=2, end_row=4, start_col=3, end_col=6)

        assert len(view) == 2
        assert len(view[0]) == 3

        view[0][0] = 'a'
        view[0][1:] = ['b', 'c']
        view[-1][:] = ['d', 'e', 'f']
        view.commit()

        assert view[1][1] == 'e'

        worksheet.refresh()
        assert worksheet[3][4] == 'e'

    finally:
        spreadsheet.delete_worksheet(worksheet_title)
        print('Removed %s' % worksheet_title)

    print('PASSED!')


if __name__ == '__main__':
    sys.exit(main())
