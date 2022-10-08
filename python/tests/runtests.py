#!/usr/bin/env python3

import os
import sys

import pytest


if __name__ == '__main__':
    print('This is deprecated! Please run pytest instead.')
    print()
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    sys.exit(pytest.main(sys.argv[1:]))
