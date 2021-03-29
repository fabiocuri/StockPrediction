#!/usr/bin/env bash
HPT="NO"
if [[ $(date +%u) -gt 5 ]]; then
 HPT="YES"
fi
#FOLDER="/home/fabiocuri/Desktop/stockprediction"
FOLDER="/home/rajaramiimb/backend"
PARAMETERS="$FOLDER/parameters_default.json"
STOCKS="$FOLDER/sp500.txt"
#virtualenv stockenv
#source stockenv/bin/activate
#pip install -r requirements.txt
while IFS= read -r line
do
  content=$line
  stock="$(cut -d'>' -f1 <<<"$content")"
  python $FOLDER/main.py $stock $PARAMETERS $HPT
done < "$STOCKS"
python $FOLDER/generate_reports.py $PARAMETERS
#python $FOLDER/accuracy.py $PARAMETERS
deactivate
