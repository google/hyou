Hyou - Pythonic Interface to manipulate Google Spreadsheet
==========================================================

Hyou provides a simple Pythonic interface to manipulate your Google
Spreadsheet data.

Synopsis
--------

.. code:: python

    import hyou
    collection = hyou.login('/path/to/credentails.json')
    spreadsheet = collection['1ZYeIFccacgHkL0TPfdgXiMfPCuEEWUtbhXvaB9HBDzQ']
    worksheet = spreadsheet['Sheet1']
    print worksheet[1][0]  # "banana"
    print worksheet[1][1]  # "50"
    worksheet[2][0] = "cinamon"
    worksheet[2][1] = 40
    worksheet.commit()

Reference
---------

TODO(nya): Write documentation.

Author
------

Shuhei Takahashi

-  Website: https://nya3.jp/
-  Twitter: https://twitter.com/nya3jp/

Disclaimer
----------

This library is authored by a Googler and copyrighted by Google, but is
not an official Google product.

License
-------

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
