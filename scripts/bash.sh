#!/usr/bin/env bash 

# cd Desktop/UW_Madison/Python/apt_finder_streeteasy_scrape
# bash scripts/bash.sh

/Users/nicholasmontalbano/opt/anaconda3/bin/python scripts/01_streeteasy.py 

/Users/nicholasmontalbano/opt/anaconda3/bin/python scripts/02_travel.py

/Users/nicholasmontalbano/opt/anaconda3/bin/python scripts/03_metrics.py

Rscript scripts/04_table.R 