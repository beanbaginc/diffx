#!/usr/bin/env python

from setuptools import setup, find_packages


PACKAGE_NAME = 'pydiffx'
VERSION = '0.1a0'


setup(name=PACKAGE_NAME,
      version=VERSION,
      license='MIT',
      description='Python module for reading and writing DiffX files.',
      url='https://github.com/beanbaginc/diffx',
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
          'Development Status :: 1 - Planning',
          'Environment :: Other Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
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
          'Topic :: Software Development :: Text Processing',
      ]
)
