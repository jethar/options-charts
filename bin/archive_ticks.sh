#!/bin/bash

rm -rf /home/harjeet/options-charts/.env
cd /home/harjeet/options-charts/data
tar czf "ticks_$(date +"%Y-%m-%d").db.tar.gz" "ticks_$(date +"%Y-%m-%d").db"

# cd /home/harjeet/options-charts/data; gsutil cp -R ticks_$(date +"%Y-%m-%d").db.tar.gz gs://finmkt-tick-data/2020/11/
