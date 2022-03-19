#!/usr/bin/env bash
python version_utils.py $*
python setup.py sdist bdist_wheel
python upload.py
python clean.py