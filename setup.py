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

from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import os

import setuptools


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read().strip()


setuptools.setup(
    name='hyou',
    version='3.0b2',
    author='Shuhei Takahashi',
    author_email='takahashi.shuhei@gmail.com',
    description='Pythonic Interface to access Google Spreadsheet',
    long_description=read_file('README.txt'),
    url='https://github.com/google/hyou/',
    packages=['hyou', 'hyou.schema'],
    scripts=[
        'tools/generate_oauth2_credentials.py',
    ],
    install_requires=read_file('requirements.txt').splitlines(),
    tests_require=read_file('requirements_dev.txt').splitlines(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
