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

import io
import itertools

import six
from six.moves import builtins


def py2_next(iter):
    return iter.next()


if six.PY2:
    bytes = builtins.str
    chr = builtins.unichr
    filter = itertools.ifilter
    input = builtins.raw_input
    map = itertools.imap
    next = py2_next
    open = io.open
    ord = builtins.ord
    range = builtins.xrange
    str = builtins.unicode
    zip = itertools.izip

else:
    bytes = builtins.bytes
    chr = builtins.chr
    filter = builtins.filter
    input = builtins.input
    map = builtins.map
    next = builtins.next
    open = io.open
    ord = builtins.ord
    range = builtins.range
    str = builtins.str
    zip = builtins.zip


def str_to_native_str(s, encoding):
    """Converts a unicode string to a native string."""
    if not isinstance(s, str):
        raise TypeError(
            'Expected %s, got %s' % (str.__name__, type(s).__name__))
    if six.PY2:
        return s.encode(encoding)
    return s


def native_str_to_bytes(s, encoding):
    """Converts a native string to a byte string."""
    if not isinstance(s, builtins.str):
        raise TypeError(
            'Expected %s, got %s' % (builtins.str.__name__, type(s).__name__))
    if six.PY2:
        return s
    return s.encode(encoding)
