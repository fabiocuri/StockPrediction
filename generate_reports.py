import sys
import json
import pyrebase
import pandas as pd
import numpy as np
from datetime import date
from collections import defaultdict, Counter
from firebase_actions import retrieve_hystoric_data

pd.set_option('display.max_columns', 1000)

if '__main__' == __name__:

    # Configuration
    params_f = str(sys.argv[1])
    export_file = str(sys.argv[2])
    
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

    ## CREATE REPORT!

    all_days = sorted(set(report["Date"]))

    # Last Day sheet
    last_day = all_days[-1]
    df_today = report[report["Date"]==last_day]

    def sum_df(df, n):

        all_stocks = []
        all_probs = []

        for stock in df["Stock"].unique():

            subset = df[df["Stock"]==stock]
            subset["Match_Trend"] = subset["Match_Trend"].astype(str)
            pctg = Counter(subset["Match_Trend"])
            value = pctg["True"]*100/(pctg["True"]+pctg["False"])

            all_stocks.append(stock)
            all_probs.append(value)

        df_sum = pd.DataFrame()
        df_sum["Stock"] = all_stocks
        df_sum[f"% Last {n} Days"] = all_probs

        return df_sum

    # Last 7 days
    date_7_days = all_days[-7:]
    df_7_days = report[report["Date"].isin(date_7_days)]
    df_7_days = sum_df(df_7_days, "7")

    # Last 14 days
    date_14_days = all_days[-14:]
    df_14_days = report[report["Date"].isin(date_14_days)]
    df_14_days = sum_df(df_14_days, "14")

    # 90% of last 14 days

    df_90 = df_14_days[df_14_days[f"% Last 14 Days"]>=90]
    df_90.columns=["Stock", f"% Last 14 Days Above 90%"]

    # 80% of last 14 days

    df_80 = df_14_days[df_14_days[f"% Last 14 Days"]>=80]
    df_80.columns=["Stock", f"% Last 14 Days Above 80%"]

    # 70% of last 14 days

    df_70 = df_14_days[df_14_days[f"% Last 14 Days"]>=70]
    df_70.columns=["Stock", f"% Last 14 Days Above 70%"]
              
    # 60% of last 14 days

    df_60 = df_14_days[df_14_days[f"% Last 14 Days"]>=60]
    df_60.columns=["Stock", f"% Last 14 Days Above 60%"]
              
    # 50% of last 14 days

    df_50 = df_14_days[df_14_days[f"% Last 14 Days"]>=50]
    df_50.columns=["Stock", f"% Last 14 Days Above 50%"]

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter("Report.xlsx", engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    df_today.to_excel(writer, sheet_name='Last Day')
    df_7_days.to_excel(writer, sheet_name='One Week')
    df_14_days.to_excel(writer, sheet_name='Two Weeks')
    df_90.to_excel(writer, sheet_name=f"90%")
    df_80.to_excel(writer, sheet_name=f"80%")
    df_70.to_excel(writer, sheet_name=f"70%")
    df_60.to_excel(writer, sheet_name=f"60%")
    df_50.to_excel(writer, sheet_name=f"50%")

    writer.save()

    if export_file == "yes":

        # Send e-mail

        from email.message import EmailMessage
        message = EmailMessage()

        sender = "stockpriceproject@gmail.com"
        recipient = "getrajaram@gmail.com"
        message['From'] = sender
        message['To'] = recipient
        message['Subject'] = f"Stock Report"

        body = """Please find attached the report for the stocks predictions."""
        message.set_content(body)

        import mimetypes
        mime_type, _ = mimetypes.guess_type(f"Report.xlsx")
        mime_type, mime_subtype = mime_type.split('/')

        with open("Report.xlsx", 'rb') as file:
            message.add_attachment(file.read(), maintype=mime_type, subtype=mime_subtype, filename=f"Report.xlsx")

        import smtplib
        mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
        mail_server.login("stockpriceproject@gmail.com", 'StockPrice2020')
        mail_server.set_debuglevel(1)
        mail_server.send_message(message)
        mail_server.quit()
