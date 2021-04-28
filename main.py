import sys
import json
import pyrebase
from get_data import get_historical_data
from models import hyperparameter_tuning_sarimax, predict_tomorrow_sarimax
from firebase_actions import retrieve_hyperparams_firebase
import warnings

warnings.filterwarnings("ignore")

if '__main__' == __name__:

    stock, params_f, hpt_bool = str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3])

    with open(params_f) as json_file:

        local_config = json.load(json_file)

    authdomain = local_config['authDomain']

    config = {"apiKey": local_config["apiKey"],
              "authDomain": f"{authdomain}.firebaseapp.com",
              "databaseURL": f"https://{authdomain}.firebaseio.com",
              "storageBucket": f"{authdomain}.appspot.com"}

    firebase_app_ = pyrebase.initialize_app(config)
    db = firebase_app_.database()

    stock_data = get_historical_data(stock=stock, years=local_config['years'])
<<<<<<< HEAD
=======
    stock_data = impute_missing_values(stock_data=stock_data)
    
    hpt_bool = "YES" ## comment
>>>>>>> f991141b7972ab08d7225de76b8312772d3d13b6

    # If weekend, tune
    if hpt_bool == "YES":

<<<<<<< HEAD
        stock_data = stock_data["GAIN_LOSS"]
        hyperparameter_tuning_sarimax(stock=stock, stock_data=stock_data, db=db)
=======
        # Retrieve only stocks lower than 100% accuracy
        report = pd.read_excel("Report.xlsx", sheet_name="All Time")
        report = report[report["% All Past Days"] < 100] ## change to 50 in the future
        critical_stocks = list(report["Stock"])

        # If stock is not critical, tune LSTM
        if stock not in critical_stocks:

            hyperparameter_tuning_lstm(stock=stock, stock_data=stock_data, length_backtesting=local_config['length_backtesting'], steps=local_config['steps'], training=local_config['training'], db=db)
>>>>>>> f991141b7972ab08d7225de76b8312772d3d13b6

    # If weekday, predict
    else:

        params = retrieve_hyperparams_firebase(stock=stock, db=db)
        predict_tomorrow_sarimax(stock=stock, stock_data=stock_data, db=db, params=params)