import sys
import json
import pyrebase
import pandas as pd
import numpy as np
from datetime import date
from collections import defaultdict
from firebase_actions import retrieve_hystoric_data

pd.set_option('display.max_columns', 1000)

if '__main__' == __name__:

    # Configuration
    params_f = str(sys.argv[1])
    
    with open(params_f) as json_file:
     
        local_config = json.load(json_file) 

    config = {"apiKey": local_config["apiKey"],
              "authDomain": f"{local_config['authDomain']}.firebaseapp.com",
              "databaseURL": f"https://{local_config['authDomain']}.firebaseio.com",
              "storageBucket": f"{local_config['authDomain']}.appspot.com"}

    firebase_app_ = pyrebase.initialize_app(config)
    db = firebase_app_.database()

    results = retrieve_hystoric_data(db)

    reports = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for stock in results.keys():
        for register in results[stock]:
            for entry in results[stock][register].keys():

                date_ = entry.split("_")[0]
                detail = '_'.join(entry.split("_")[1:])
                value = results[stock][register][entry]

                reports[stock][date_][detail] = value

    list_report = list()

    for stock in reports.keys():
        for date_ in reports[stock].keys():

            list_report.append(
                [stock, date_, reports[stock][date_]["REAL_Price"], reports[stock][date_]["REAL_Price_Diff"],
                reports[stock][date_]["REAL_Price_Trend"], reports[stock][date_]["PRED_Price"],
                reports[stock][date_]["PRED_Price_Diff"], reports[stock][date_]["PRED_Price_Trend"]]
                )

    report = pd.DataFrame(list_report, columns=["Stock", "Date", "REAL_Price", "REAL_Price_Diff", "REAL_Price_Trend", "PRED_Price", "PRED_Price_Diff", "PRED_Price_Trend"])
    report.sort_values(by=['Stock', 'Date'], ascending=True, inplace=True)

    report = report.mask(report.applymap(str).eq('[]'))
    report.dropna(inplace=True)
    report["Match_Trend"] = report["REAL_Price_Trend"] == report["PRED_Price_Trend"]

    today = date.today()
    date = today.strftime("%d-%m-%Y")

    report.to_csv(f"Stocks_Prediction_Report_{date}.csv", index=None)