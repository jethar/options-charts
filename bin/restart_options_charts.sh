#!/bin/bash

cd /home/harjeet/options-charts
source venv/bin/activate
kill $(pgrep python)
source <(grep -v '^#' .env | sed -E 's|^(.+)=(.*)$|: ${\1=\2}; export \1|g')
rm -rf .env
cd /home/harjeet/options-charts/src/options_charts
python ticker_fullmode.py
