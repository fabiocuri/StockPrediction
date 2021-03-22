import sys
import json
import pyrebase
import numpy as np
from get_data import get_historical_data
from models import impute_missing_values, hyperparameter_tuning, predict_tomorrow

if '__main__' == __name__:

    # Configuration
    stock, params_f = str(sys.argv[1]), str(sys.argv[2])
    
    with open(params_f) as json_file:
     
        local_config = json.load(json_file) 

    config = {"apiKey": local_config["apiKey"],
              "authDomain": f"{local_config['authDomain']}.firebaseapp.com",
              "databaseURL": f"https://{local_config['authDomain']}.firebaseio.com",
              "storageBucket": f"{local_config['authDomain']}.appspot.com"}

    firebase_app_ = pyrebase.initialize_app(config)
    db = firebase_app_.database()

    # db.child("XGBOOST_HYPERPARAMS").remove()
    # db.child("HISTORY_PREDS").remove()
    # db.child("CURRENT_PREDS").remove()
    # sys.exit()

    # Get stock data
    stock_data = get_historical_data(stock=stock, years=local_config['years'])
    
    # Missing values imputation
    stock_data = impute_missing_values(stock_data=stock_data)

    # Hyper-parameter tuning
    hyperparameter_tuning(stock=stock, stock_data=stock_data, years=local_config['years'],
                          length_backtesting=local_config['length_backtesting'], steps=local_config['steps'], training=local_config['training'], db=db)

    # Run predictions for the past
    runs = ["all"]
    runs.extend(list((np.array(range(14)) + 1) * -1))

    for i in runs:

        if i == "all":

            subset_data = stock_data

        else:

            subset_data = stock_data[:i]

        # Predict next day
        predict_tomorrow(stock=stock, stock_data=subset_data, steps=local_config['steps'],
                        training=local_config['training'], db=db)