#!/bin/bash

if [[ $(ps -ef | grep ticker | wc -l) -lt 2 ]]
 then
 	cd /home/harjeet/options-charts
	source venv/bin/activate
	source <(grep -v '^#' .env | sed -E 's|^(.+)=(.*)$|: ${\1=\2}; export \1|g')
	touch RESTARTED_$(date +"%Y-%m-%d_%H-%M-%S")
	# rm -rf .env
	cd /home/harjeet/options-charts/src/options_charts
	python ticker_fullmode.py
fi
