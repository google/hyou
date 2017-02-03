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
from builtins import (  # noqa: F401
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next,
    object, oct, open, pow, range, round, str, super, zip)

import hashlib
import httplib2
import json
import logging
import os

from future.moves.urllib import parse

import hyou.util


RECORDS_DIR = os.path.join(os.path.dirname(__file__), 'records')

ENV_RECORD = os.environ.get('HYOU_TEST_RECORD')
ENV_CREDENTIALS = os.environ.get('HYOU_TEST_CREDENTIALS')


def _canonicalize_uri(uri):
    scheme, netloc, path, params, query, fragment = parse.urlparse(uri)
    if query:
        query = parse.urlencode(sorted(parse.parse_qsl(query)))
    return parse.urlunparse((scheme, netloc, path, params, query, fragment))


def _canonicalize_json(body_json):
    # body_json can be bytes or str.
    if isinstance(body_json, str):
        json_str = body_json
    else:
        json_str = body_json.decode('utf-8')
    json_data = json.loads(json_str)
    canonicalized_json_binary = json.dumps(
        json_data, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return canonicalized_json_binary


def _build_signature(method, uri, body):
    sig = '%s %s' % (method, _canonicalize_uri(uri))
    if body is not None:
        sig += ' %s' % hashlib.sha1(_canonicalize_json(body)).hexdigest()
    return sig


def _load_records():
    records = {}
    for filename in sorted(os.listdir(RECORDS_DIR)):
        record_path = os.path.join(RECORDS_DIR, filename)
        with open(record_path, 'r', encoding='utf-8') as f:
            record = json.load(f)
            record['_path'] = record_path
            body_bytes = (
                record['request'].encode('utf-8')
                if record['request']
                else None)
            sig = _build_signature(
                method=record['method'],
                uri=record['uri'],
                body=body_bytes)
            assert sig not in records, 'dup response: %s' % filename
            records[sig] = record
    return records


def _make_ok_response():
    return httplib2.Response({'status': 200})


class ReplayHttp(object):

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._real_http = httplib2.Http()
        if ENV_CREDENTIALS:
            with open(ENV_CREDENTIALS) as f:
                credentials = hyou.util.parse_credentials(f.read())
            self._real_http = credentials.authorize(self._real_http)
        self._records = _load_records()

    def request(self, uri, method='GET', body=None, *args, **kwargs):
        sig = _build_signature(method=method, uri=uri, body=body)

        if sig in self._records:
            record = self._records[sig]
            logging.info('Returning a recorded response: %s', record['_path'])
            response_body = record['response'].encode('utf-8')
            return (_make_ok_response(), response_body)

        if ENV_RECORD != '1':
            logging.error('Response not available!')
            logging.error('Requested: %s', sig)
            for s in sorted(self._records.keys()):
                logging.error('Candidate: %s', s)
            raise Exception(
                'Response not available; run unit tests with '
                'HYOU_TEST_RECORD=1.')

        response_headers, response_body = self._real_http.request(
            uri, method, body, *args, **kwargs)
        if response_headers.status != 200:
            raise Exception(
                'Got status=%d; maybe you need to set '
                'HYOU_TEST_CREDENTIALS?\n%s'
                % (response_headers.status, response_body))

        record = {
            'method': method,
            'uri': uri,
            'request': body,
            'response': response_body.decode('utf-8'),
        }
        sig_hash = hashlib.sha1(sig).hexdigest()
        record_path = os.path.join(RECORDS_DIR, '%s.json' % sig_hash)
        with open(record_path, 'w') as f:
            json.dump(record, f)

        logging.info('Recorded a response: %s', record_path)

        record['_path'] = record_path
        self._records[sig] = record

        # Do not return |response_headers| for consistency on replay.
        return (_make_ok_response(), response_body)
