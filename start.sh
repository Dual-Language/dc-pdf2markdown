#!/bin/bash
set -e

pip install --upgrade pip

pip install -r requirements-base1.txt
pip install -r requirements-base2.txt
pip install -r requirements-base3.txt
pip install -r requirements-base4-1.txt
pip install -r requirements-base4-2.txt
pip install -r requirements-base4-3.txt
pip install -r requirements-base4-4.txt
pip install -r requirements-marker.txt

python main.py 