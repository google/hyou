Hyou Documentation
==================

Hyou provides a simple Pythonic interface to access your Google Spreadsheet data.

|PyPI version| |Build Status| |Coverage Status|


.. py:currentmodule:: hyou


Synopsis
--------

.. code:: python

    import hyou

    # Login to Google Spreadsheet with credentials
    collection = hyou.login('/path/to/credentails.json')

    # Open a spreadsheet by ID
    spreadsheet = collection['1ZYeIFccacgHkL0TPfdgXiMfPCuEEWUtbhXvaB9HBDzQ']
    print spreadsheet.title         # => "Hyou Test Sheet"

    # Open a worksheet in a spreadsheet by sheet name
    worksheet = spreadsheet['Sheet1']
    print worksheet.title           # => "Sheet1"
    print worksheet.rows            # => 5
    print worksheet.cols            # => 3

    # Worksheet objects can be accessed just like two-dimensional lists
    print worksheet[1][0]           # => "banana"
    print worksheet[1][1]           # => "50"

    # Call Worksheet.commit() to apply changes
    worksheet[2][0] = 'cinamon'
    worksheet[2][1] = 40
    worksheet.commit()


User Guide
----------


Installation
~~~~~~~~~~~~

Hyou can be installed from pypi with pip.

.. code::

    $ sudo pip install hyou
    or
    $ pip install --user hyou

Source code is available on GitHub.

https://github.com/google/hyou


Preparing Credentials
~~~~~~~~~~~~~~~~~~~~~

The first step is to prepare a credential you access Google Spreadsheet with.

There are three options:

1. Authorize as your Google account with OAuth2 using a shared application project.
2. Authorize as your Google account with OAuth2 using your own application project.
3. Authorize as a service account (a bot account not associated with any Google account).

If you just want to access your spreadsheet programatically, 1 is the safe and easy way. In other options, you need some steps to register an application at Google Developer Console. (TODO(nya): Describe those options too)

To authorize as your Google account with a shared application project, run ``generate_oauth2_credentials.py``.

.. code::

    $ generate_oauth2_credentials.py ~/.drive.json
    Please visit this URL to get the authorization code:
    https://accounts.google.com/o/oauth2/auth?scope=...

    Code:_

Open the URL with a web browser, click "Accept" button, copy-and-paste the authorization code to the console and hit enter. Then the credential JSON is saved to the specified file.

Keep the credential file in a safe location. With the credentials, all your Google Drive documents can be accessed.

Once you prepared a credential JSON file, it is very simple to connect to Google Spreadsheet service using it:

.. code:: python

    collection = hyou.login('/path/to/credentails.json')


Working with Collections
~~~~~~~~~~~~~~~~~~~~~~~~

A :py:class:`Collection` object represents a set of Google Spreadsheet documents. It is a dictionary-like object, whose key is spreadsheet ID and value is a :py:class:`Spreadsheet` object.

You can enumerate the spreadsheets you own by accessing a :py:class:`Collection` object like a dictionary.

.. code:: python

    for id, spreadsheet in collection.iteritems():
        print id, spreadsheet.title

If you know a spreadsheet ID, you can open it just by indexing. This is faster than iterating through :py:class:`Collection` because it does not fetch the list of spreadsheets. For example, to open https://docs.google.com/spreadsheets/d/1ZYeIFccacgHkL0TPfdgXiMfPCuEEWUtbhXvaB9HBDzQ/edit :

.. code:: python

    spreadsheet = collection['1ZYeIFccacgHkL0TPfdgXiMfPCuEEWUtbhXvaB9HBDzQ']


Working with Spreadsheets
~~~~~~~~~~~~~~~~~~~~~~~~~

A :py:class:`Spreadsheet` object is an ordered dictionary-like object, whose key is a worksheet title and value is a :py:class:`Worksheet` object.

.. code:: python

    worksheet = spreadsheet['Sheet1']

It also behaves just like a list when accessed with integer indices since it is ordered.

.. code:: python

    worksheet = spreadsheet[0]  # Open the first worksheet

To add or delete worksheets, use :py:meth:`Spreadsheet.add_worksheet` and :py:meth:`Spreadsheet.delete_worksheet`.

.. code:: python

    new_worksheet = spreadsheet.add_worksheet('worksheet title', rows=1000, cols=26)
    spreadsheet.delete_worksheet('worksheet title')

:py:attr:`Spreadsheet.title` read-write property holds the title of the spreadsheet.

.. code:: python

    print spreadsheet.title  # => "Current spreadsheet name"
    spreadsheet.title = 'New spreadsheet name'


Working with Worksheets
~~~~~~~~~~~~~~~~~~~~~~~

A :py:class:`Worksheet` object can be accessed just like two-dimensional string lists.

.. code:: python

    for i, row in enumerate(worksheet):
        print i, row[0], '/'.join(row[1:])

A cell value is a bare input string, represented as a unicode string (:py:class:`str` in Python 3, :py:class:`unicode` in Python 2).

- Numbers are converted to strings.
- Formulas (e.g. `"=SUM(A2:A)"`) are never expanded, and returned as-is.

Inversely, you can create a formula cell by writing a formula string like `"=SUM(A2:A)"`.

If you attempt to write a non-string value (e.g. numbers) to a cell, it is automatically converted to a string.

.. code:: python

    worksheet[0][0] = 7
    print type(worksheet[0][0])  # => str in Python 3, unicode in Python 2

Writes to cells are never committed until :py:meth:`Worksheet.commit` is called. You can use *with statements* to make sure :py:meth:`Worksheet.commit` is called:

.. code:: python

    with worksheet:
        worksheet[0][0] = 'apple'
        worksheet[1][0] = 'banana'
        worksheet[2][0] = 'cinamon'
    # Changes have been committed at this point


.. _cache-behavior-section:

Cache Behavior
~~~~~~~~~~~~~~

To reduce network traffic and round-trips, data is fetched on demand and cached. For example, calling :py:meth:`Worksheet.values()` first time takes some time to fetch data to servers, but subsequent calls return immediately because the server response is cached.

To clear the cache to access the up-to-date data, call :py:func:`refresh`.

Please be aware that any uncommitted writes to worksheet cells are discarded when :py:func:`refresh` is called.

As for :py:class:`Worksheet`, all worksheet cells are fetched when a cell is attempted to read for the first time. This can be waste of time and bandwidth if you are interested in a subrange of a worksheet. In such case, you can use views described next.


Using Views
~~~~~~~~~~~

If you are interested in a subrange of a worksheet, you can use :py:class:`WorksheetView` for efficiency to reduce the number of fetched cells. For example, this code snippet will create a 20x10 view of a worksheet:

.. code:: python

    view = worksheet.view(start_row=100, end_row=120, start_col=200, end_col=210)
    assert view[0][0] == worksheet[100][200]

Each view has independent cache. Reading a cell of a view will fetch contained cells only, instead of all cells in the worksheet.


API Reference
-------------

.. data:: SCOPES

   A tuple of strings representing the scopes needed to access spreadsheets.
   Use this constant to request OAuth2 credentials.


.. function:: login(json_path=None, json_text=None)

   Logs in to Google Spreadsheet, and returns a new :py:class:`Collection` object.

   :param str json_path: The filesystem path to a credential JSON file.
   :param str json_text: A credential JSON in text format.

   Either one of `json_path` or `json_text` should be given.

   This method accepts two formats of credential JSONs:

   1. JSON file that serialized :py:class:`oauth2client.client.Credentials`.
   2. JSON file downloaded from Google Developer Console (for service accounts)


.. class:: Collection

   Representation of your spreadsheet collection.

   This is a dictionary-like object, implementing several dictionary methods like
   :py:meth:`keys`, :py:meth:`values`, :py:meth:`items`,
   :py:meth:`iterkeys`, :py:meth:`itervalues`, :py:meth:`iteritems`,
   :py:meth:`__len__`, :py:meth:`__iter__`.
   In contrast to usual :py:class:`dict`, it is immutable (unless :py:meth:`refresh` is called).

   .. classmethod:: login(json_path=None, json_text=None)

      An alias of :py:func:`login`.

   .. method:: create_spreadsheet(title, rows=1000, cols=26)

      Creates a new spreadsheet, and returns a :py:class:`Spreadsheet` instance.

      :param str title: The title of a new spreadsheet.
      :param int rows: The number of rows of a new spreadsheet.
      :param int cols: The number of cols of a new spreadsheet.

      Addition of a spreadsheet is committed immediately and :py:meth:`refresh` is automatically called to reflect changes.

   .. method:: refresh()

      Discards the associated cache. See :ref:`cache-behavior-section` for details.


.. class:: Spreadsheet

   Representation of a spreadsheet.

   This is a dictionary-like object, implementing several dictionary methods like
   :py:meth:`keys`, :py:meth:`values`, :py:meth:`items`,
   :py:meth:`iterkeys`, :py:meth:`itervalues`, :py:meth:`iteritems`,
   :py:meth:`__len__`, :py:meth:`__iter__`.
   In contrast to usual :py:class:`dict`, it is immutable (unless :py:meth:`refresh` is called), and elements are ordered.

   Ordered values can by accessed by indices. That is, ``obj[i]`` is equivalent to ``obj.values()[i]`` when ``i`` is an integer.

   .. attribute:: key

      The spreadsheet ID.

      This property is read-only.

   .. attribute:: title

      The title of the spreadsheet.

      This property is writable. Writes are committed immediately and :py:meth:`refresh` is automatically called to reflect changes.

   .. attribute:: url

      The URL of the spreadsheet.

      This property is read-only.

   .. attribute:: updated

      The last update time of the spreadsheet as a :py:class:`datetime.datetime` object.

      This property is read-only.

   .. method:: add_worksheet(title, rows=100, cols=26)

      Adds a new worksheet and returns a new :py:class:`Worksheet` object.

      :param str title: The title of a new worksheet.
      :param int rows: The number of rows of a new worksheet.
      :param int cols: The number of cols of a new worksheet.

      Addition of a worksheet is committed immediately and :py:meth:`refresh` is automatically called to reflect changes.

   .. method:: delete_worksheet(title)

      Deletes a worksheet.

      :param str title: The title of the worksheet to be deleted.

      Deletion of a worksheet is committed immediately and :py:meth:`refresh` is automatically called to reflect changes.

   .. method:: refresh()

      Discards the associated cache. See :ref:`cache-behavior-section` for details.


.. class:: Worksheet

   Representation of a worksheet.

   This object behaves just like two-dimensional string lists. The first dimension is rows and the second is columns.

   .. attribute:: title

      The title of the worksheet.

      This property is writable. Writes are committed immediately and :py:meth:`refresh` is automatically called to reflect changes.

   .. attribute:: rows

      The number of rows of the worksheet.

      This property is writable. Writes are committed immediately and :py:meth:`refresh` is automatically called to reflect changes.

      Use :py:meth:`set_size` to change the number of both rows and columns simultaneously.

   .. attribute:: cols

      The number of columns of the worksheet.

      This property is writable. Writes are committed immediately and :py:meth:`refresh` is automatically called to reflect changes.

      Use :py:meth:`set_size` to change the number of both rows and columns simultaneously.

   .. method:: commit()

      Commits writes to cells. Until this method is called, writes to cells never take effect.

   .. method:: __enter__
   .. method:: __exit__

      These methods implements context manager protocol to make sure :py:meth:`commit` is called.

   .. method:: set_size(rows, cols)

      Changes the dimension of the worksheet.

      :param int rows: The new number of rows.
      :param int cols: The new number of cols.

      Changes are committed immediately and :py:meth:`refresh` is automatically called to reflect changes.

   .. method:: view(start_row=None, end_row=None, start_col=None, end_col=None)

      Creates a new :py:class:`WorksheetView` representing a subrange of the worksheet.

      :param integer start_row: The index of the first row included in a new view. Defaults to 0 if not specified.
      :param integer end_row: The index of the first row NOT included in a new view. Default to :py:attr:`rows` if not specified.
      :param integer start_col: The index of the first column included in a new view. Defaults to 0 if not specified.
      :param integer end_col: The index of the first column NOT included in a new view. Default to :py:attr:`cols` if not specified.

   .. method:: refresh()

      Discards the associated cache. Please be aware that any uncommitted writes to cells are also discarded. See :ref:`cache-behavior-section` for details.


.. class:: WorksheetView

   Representation of a subrange of a worksheet.

   Similarly as :py:class:`Worksheet`, this object behaves just like two-dimensional string lists.

   .. attribute:: rows

      The number of rows in this view. Read-only.

   .. attribute:: cols

      The number of columns in this view. Read-only.

   .. method:: commit()

      Commits writes to cells. Until this method is called, writes to cells never take effect.

   .. method:: __enter__
   .. method:: __exit__

      These methods implements context manager protocol to make sure :py:meth:`commit` is called.

   .. method:: refresh()

      Discards the associated cache. Please be aware that any uncommitted writes to cells are also discarded. See :ref:`cache-behavior-section` for details.


Changelog
---------

3.0.0 (2017-02-XX)

- Added Python 3.3+ support.
- Dropped Python 2.6 support.
- Switched to Sheets API v4.
- Now cell values are always represented as a unicode string even in Python 2.

2.1.1 (2016-07-04)

- Support oauth2client v2.0.0+.

2.1.0 (2015-10-28)

- Worksheets emulate standard lists better.
- Support Python 2.6.
- Bugfixes.

2.0.0 (2015-08-14)

- First stable release with 100% test coverage.

1.x

- Beta releases.


Notices
-------


Author
~~~~~~

Shuhei Takahashi

-  Website: https://nya3.jp/
-  Twitter: https://twitter.com/nya3jp/

Disclaimer
~~~~~~~~~~

This library is authored by a Googler and copyrighted by Google, but is
not an official Google product.

License
~~~~~~~

Copyright 2015 Google Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

::

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


.. |PyPI version| image:: https://badge.fury.io/py/hyou.svg
   :target: http://badge.fury.io/py/hyou
.. |Build Status| image:: https://travis-ci.org/google/hyou.svg
   :target: https://travis-ci.org/google/hyou
.. |Coverage Status| image:: https://coveralls.io/repos/google/hyou/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/google/hyou?branch=master
