#!/usr/bin/env bash
FOLDER="/home/fabiocuri/Desktop/stock"
#FOLDER="/home/rajaramiimb2/backend"
PARAMETERS="$FOLDER/parameters_default.json"
python $FOLDER/generate_reports.py $PARAMETERS
deactivate
