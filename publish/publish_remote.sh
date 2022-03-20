#!/usr/bin/env bash
set -e
python version_utils.py -l remote $*
python setup.py sdist bdist_wheel
python upload.py
python clean.py