#!/usr/bin/env bash
FOLDER="/home/fabiocuri/Desktop/stock"
#FOLDER="/home/rajaramiimb2/backend"
PARAMETERS="$FOLDER/parameters_default.json"
STOCKS="$FOLDER/sp500.txt"
virtualenv stockenv
source stockenv/bin/activate
#pip install -r requirements.txt
while IFS= read -r line
do
  content=$line
  stock="$(cut -d'>' -f1 <<<"$content")"
  python $FOLDER/main.py $stock $PARAMETERS
done < "$STOCKS"
#python $FOLDER/accuracy.py $PARAMETERS
deactivate
