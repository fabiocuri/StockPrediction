import sys
import json
import pyrebase
import numpy as np
from get_data import get_historical_data
from models import impute_missing_values, hyperparameter_tuning, predict_tomorrow

if '__main__' == __name__:

    # Configuration
    stock, params_f, hpt_bool = str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3])
    
    print(stock)
    
    with open(params_f) as json_file:
     
        local_config = json.load(json_file) 
        
    authdomain = local_config['authDomain']

    config = {"apiKey": local_config["apiKey"],
              "authDomain": f"{authdomain}.firebaseapp.com",
              "databaseURL": f"https://{authdomain}.firebaseio.com",
              "storageBucket": f"{authdomain}.appspot.com"}

    firebase_app_ = pyrebase.initialize_app(config)
    db = firebase_app_.database()

    # db.child("XGBOOST_HYPERPARAMS").remove()
    # db.child("HISTORY_PREDS").remove()
    # db.child("CURRENT_PREDS").remove()
    # sys.exit()

    stock_data = get_historical_data(stock=stock, years=local_config['years'])
    stock_data = impute_missing_values(stock_data=stock_data)

    if hpt_bool == "YES":

        hyperparameter_tuning(stock=stock, stock_data=stock_data, years=local_config['years'],
                            length_backtesting=local_config['length_backtesting'], steps=local_config['steps'], training=local_config['training'], db=db)

    for i in [-1]:
    
        subset_stock_data = stock_data[:i]

        # Predict next day
        predict_tomorrow(stock=stock, stock_data=subset_stock_data, steps=local_config['steps'],
                        training=local_config['training'], db=db)
                        
    predict_tomorrow(stock=stock, stock_data=stock_data, steps=local_config['steps'],
                    training=local_config['training'], db=db)
                        
                        
