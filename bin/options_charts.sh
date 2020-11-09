#!/bin/bash

cd /home/harjeet/options-charts
source venv/bin/activate
source <(grep -v '^#' .env | sed -E 's|^(.+)=(.*)$|: ${\1=\2}; export \1|g')
cd /home/harjeet/options-charts/src/options_charts
python ticker.py
