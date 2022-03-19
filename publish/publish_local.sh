#!/usr/bin/env bash
set -e
python version_utils.py -l local $*
python setup.py sdist bdist_wheel && pip install dist/*.whl
python clean.py