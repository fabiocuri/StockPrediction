#!/usr/bin/env bash
HPT="NO"
if [[ $(date +%u) -gt 5 ]]; then
 HPT="YES"
fi
FOLDER="/home/rajaramiimb/backend"
PARAMETERS="$FOLDER/parameters_default.json"
STOCKS="$FOLDER/sp500_machine1.txt"
while IFS= read -r line
do
  content=$line
  stock="$(cut -d'>' -f1 <<<"$content")"
  python3.7 $FOLDER/main.py $stock $PARAMETERS $HPT
done < "$STOCKS"
