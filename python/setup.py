#!/usr/bin/env python

from __future__ import unicode_literals

import os
import subprocess
import sys

from setuptools import setup, find_packages

from pydiffx import get_package_version


PACKAGE_NAME = 'pydiffx'

# NOTE: When updating, make sure you update the classifiers below.
SUPPORTED_PYVERS = ['2.7', '3.6', '3.7', '3.8', '3.9']


if '--all-pyvers' in sys.argv:
    new_argv = sys.argv[1:]
    new_argv.remove('--all-pyvers')

    for pyver in SUPPORTED_PYVERS:
        result = os.system(subprocess.list2cmdline(
            ['python%s' % pyver, __file__] + new_argv))

        if result != 0:
            sys.exit(result)

    sys.exit(0)


with open('README.rst', 'r') as fp:
    long_description = fp.read()


setup(name=PACKAGE_NAME,
      version=get_package_version(),
      license='MIT',
      description='Python module for reading and writing DiffX files.',
      long_description=long_description,
      author='Beanbag, Inc.',
      author_email='questions@beanbaginc.com',
      url='https://diffx.org/pydiffx/',
      packages=find_packages(),
      maintainer='Christian Hammond',
      maintainer_email='christian@beanbaginc.com',
      install_requires=[
          'six',
      ],
      entry_points={
          'pygments.lexers': [
              'diffx = pydiffx.integrations.pygments_lexer:DiffXLexer',
          ],
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Other Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Version Control',
          'Topic :: Text Processing',
          'Topic :: Text Processing :: General',
      ]
)
