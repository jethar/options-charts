#!/bin/bash

cd /home/harjeet/options-charts/data
tar czf "ticks_$(date +"%Y-%m-%d").db.tar.gz" "ticks_$(date +"%Y-%m-%d").db"
