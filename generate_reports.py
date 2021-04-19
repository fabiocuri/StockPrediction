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

    today = date.today()
    date = today.strftime("%d-%m-%Y")

    all_days = sorted(set(report["Date"]))

    # Last Day sheet
    date_today = today.strftime("%Y-%m-%d")
    df_today = report[report["Date"]==all_days[-1]]

    # Last 7 days
    date_7_days = all_days[-7:]
    df_7_days = report[report["Date"].isin(date_7_days)]

    all_stocks = []
    all_probs = []

    for stock in df_7_days["Stock"].unique():

        subset = df_7_days[df_7_days["Stock"]==stock]
        subset["Match_Trend"] = subset["Match_Trend"].astype(str)
        pctg = Counter(subset["Match_Trend"])
        value = pctg["True"]*100/(pctg["True"]+pctg["False"])

        all_stocks.append(stock)
        all_probs.append(value)

    df_7_days = pd.DataFrame()
    df_7_days["Stock"] = all_stocks
    df_7_days[f"% Last 7 Days"] = all_probs

    # Last 14 days
    date_14_days = all_days[-14:]
    df_14_days = report[report["Date"].isin(date_14_days)]

    all_stocks = []
    all_probs = []

    for stock in df_14_days["Stock"].unique():

        subset = df_14_days[df_14_days["Stock"]==stock]
        subset["Match_Trend"] = subset["Match_Trend"].astype(str)
        pctg = Counter(subset["Match_Trend"])
        value = pctg["True"]*100/(pctg["True"]+pctg["False"])

        all_stocks.append(stock)
        all_probs.append(value)

    df_14_days = pd.DataFrame()
    df_14_days["Stock"] = all_stocks
    df_14_days[f"% Last 14 Days"] = all_probs

    # All time

    all_stocks = []
    all_probs = []

    for stock in report["Stock"].unique():

        subset = report[report["Stock"]==stock]
        subset["Match_Trend"] = subset["Match_Trend"].astype(str)
        pctg = Counter(subset["Match_Trend"])
        value = pctg["True"]*100/(pctg["True"]+pctg["False"])

        all_stocks.append(stock)
        all_probs.append(value)

    df_all_time = pd.DataFrame()
    df_all_time["Stock"] = all_stocks
    df_all_time[f"% All Past Days"] = all_probs

    # 90%

    df_90 = df_all_time[df_all_time[f"% All Past Days"]>=90]
    df_90.columns=["Stock", "% All Past Days Above 90%"]

    # 80%

    df_80 = df_all_time[df_all_time[f"% All Past Days"]>=80]
    df_80.columns=["Stock", "% All Past Days Above 80%"]

    # 70%

    df_70 = df_all_time[df_all_time[f"% All Past Days"]>=70]
    df_70.columns=["Stock", "% All Past Days Above 70%"]
              
    # 60%

    df_60 = df_all_time[df_all_time[f"% All Past Days"]>=60]
    df_60.columns=["Stock", "% All Past Days Above 60%"]
              
    # 50%

    df_50 = df_all_time[df_all_time[f"% All Past Days"]>=50]
    df_50.columns=["Stock", "% All Past Days Above 50%"]

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter("Report.xlsx", engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    df_today.to_excel(writer, sheet_name='Last Day')
    df_7_days.to_excel(writer, sheet_name='One Week')
    df_14_days.to_excel(writer, sheet_name='Two Weeks')
    df_all_time.to_excel(writer, sheet_name='All Time')
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
        message['Subject'] = f"Stock Report {today}"

        body = """Please find attached the report for the stocks predictions."""
        message.set_content(body)

        import mimetypes
        mime_type, _ = mimetypes.guess_type(f"Report_{today}.xlsx")
        mime_type, mime_subtype = mime_type.split('/')

        with open("Report.xlsx", 'rb') as file:
            message.add_attachment(file.read(), maintype=mime_type, subtype=mime_subtype, filename=f"Report_{today}.xlsx")

        import smtplib
        mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
        mail_server.login("stockpriceproject@gmail.com", 'StockPrice2020')
        mail_server.set_debuglevel(1)
        mail_server.send_message(message)
        mail_server.quit()
