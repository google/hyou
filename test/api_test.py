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

import contextlib
import logging
import unittest

import hyou.api

import http_mocks


@contextlib.contextmanager
def suppress_oauth2client_warnings():
    """Suppresses warnings from oauth2client 4+."""
    logger = logging.getLogger('googleapiclient.discovery_cache')
    logger.setLevel(logging.ERROR)
    try:
        yield
    finally:
        logger.setLevel(logging.NOTSET)


class APITest(unittest.TestCase):

    def test_no_discovery(self):
        hyou.api.API(
            http_mocks.ReplayHttp(None),
            discovery=False)

    def test_discovery(self):
        with suppress_oauth2client_warnings():
            hyou.api.API(
                http_mocks.ReplayHttp('unittest-collection.json'),
                discovery=True)
