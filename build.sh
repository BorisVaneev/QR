#!/usr/bin/env bash
pip install --upgrade pip
pip install -r requirements.txt
python -m venv venv
source venv/bin/activate
which gunicorn  #
