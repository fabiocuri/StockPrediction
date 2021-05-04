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

    # If weekend, tune
    if hpt_bool == "YES":

        stock_data = stock_data["GAIN_LOSS"]
        hyperparameter_tuning_sarimax(stock=stock, stock_data=stock_data, db=db)

    # If weekday, predict
    else:

        params = retrieve_hyperparams_firebase(stock=stock, db=db)
        predict_tomorrow_sarimax(stock=stock, stock_data=stock_data, db=db, params=params)