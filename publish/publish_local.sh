#!/usr/bin/env bash
python version_utils.py $*
python setup.py sdist bdist_wheel && pip install dist/*.whl
python clean.py