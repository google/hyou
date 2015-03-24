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

class LazyOrderedDictionary(object):
  def __init__(self, enumerator, constructor):
    self._enumerator = enumerator
    self._constructor = constructor
    self._cache_list = []   # [(key, value)]
    self._cache_index = {}  # key -> index of _cache_list
    self._enumerated = False

  def refresh(self):
    del self._cache_list[:]
    self._cache_index.clear()
    self._enumerated = False

  def __len__(self):
    self._ensure_enumerated()
    return len(self._cache_list)

  def __iter__(self):
    return self.iterkeys()

  def iterkeys(self):
    self._ensure_enumerated()
    for key, _ in self._cache_list:
      yield key

  def itervalues(self):
    self._ensure_enumerated()
    for _, value in self._cache_list:
      yield value

  def iteritems(self):
    self._ensure_enumerated()
    for item in self._cache_list:
      yield item

  def keys(self):
    return list(self.iterkeys())

  def values(self):
    return list(self.itervalues())

  def items(self):
    return list(self.iteritems())

  def __getitem__(self, key):
    if isinstance(key, int):
      self._ensure_enumerated()
      return self._cache_list[key][1]
    index = self._cache_index.get(key)
    if index is None and self._constructor:
      try:
        value = self._constructor(key)
      except Exception:
        pass
      else:
        assert value is not None
        index = len(self._cache_list)
        self._cache_index[key] = index
        self._cache_list.append((key, value))
        return value
    self._ensure_enumerated()
    index = self._cache_index.get(key)
    if index is None:
      raise KeyError(key)
    return self._cache_list[index][1]

  def _ensure_enumerated(self):
    if not self._enumerated:
      # Save partially constructed entries.
      saves = self._cache_list[:]
      # Initialize cache with the enumerator.
      del self._cache_list[:]
      self._cache_index.clear()
      for key, value in self._enumerator():
        self._cache_index[key] = len(self._cache_list)
        self._cache_list.append((key, value))
      # Restore saved entries.
      for key, value in saves:
        index = self._cache_index.get(key)
        if index is None:
          index = len(self._cache_list)
          self._cache_list.append((None, None))
        self._cache_list[index] = (key, value)
      self._enumerated = True


class CustomImmutableList(object):
  """Provides methods to mimic a immutable Python list.

  Subclasses need to provide implementation of at least following methods:
  - __getitem__
  - __iter__
  - __len__
  """

  def __contains__(self, find_value):
    for i, value in enumerate(self):
      if value == find_value:
        return True
    return False

  def index(self, find_value):
    for i, value in enumerate(self):
      if value == find_value:
        return i
    raise ValueError('%r is not in list' % find_value)

  def count(self, find_value):
    result = 0
    for value in self:
      if value == find_value:
        result += 1
    return result


class CustomMutableFixedList(CustomImmutableList):
  """Provides methods to mimic a mutable Python list.

  Subclasses need to provide implementation of at least following methods,
  in addition to those required by CustomImmutableList:
  - __setitem__
  """

  def sort(self, cmp=None, key=None, reverse=False):
    for i, new_value in sorted(self, cmp=cmp, key=key, reverse=reverse):
      self[i] = new_value
