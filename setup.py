##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for zope.index package

$Id$
"""

import os

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.index',
      version='3.4-dev',
      url='http://svn.zope.org/zope.index',
      license='ZPL 2.1',
      description='Zope index',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="Indices for using with catalog like text, field, etc.",

      packages=['zope',
                'zope.index',
                'zope.index.field',
                'zope.index.keyword',
                'zope.index.text',
                'zope.index.topic',
                'zope.index.topic.tests'],
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['BTrees',
                        'ZODB',
                        'persistent',
                        'transaction',
                        'zope.interface'],
      include_package_data = True,

      zip_safe = False,
      )
