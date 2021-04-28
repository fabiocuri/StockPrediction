import numpy as np
import datetime as dt
from statsmodels.tsa.arima.model import ARIMA
from pmdarima.arima import auto_arima
import warnings
from firebase_actions import export_firebase

warnings.simplefilter(action='ignore', category=FutureWarning)
np.random.seed(0)


def format_floats(value, n):
    return str(round(value, n))


def get_dates(stock_data):
    """
    Gets today value and next labor date.
    """

    last_date_str = stock_data.index[-1]
    last_date = dt.datetime.strptime(str(last_date_str), '%Y-%m-%d %H:%M:%S')
    next_date = (last_date + dt.timedelta(days=1))

    while next_date.weekday() == 5 or next_date.weekday() == 6:
        next_date = next_date + dt.timedelta(days=1)

    next_date = next_date.strftime('%Y-%m-%d')

    last_date_str = str(last_date_str).split(" ")[0]

    return last_date_str, next_date


def hyperparameter_tuning_sarimax(stock, stock_data, db):
    """
    Hyper-parameter tuning with back-testing for SARIMAX.
    """

    stepwise_model = auto_arima(stock_data, start_p=1, start_q=1,
                                max_p=2, max_q=2, m=12,
                                start_P=0, seasonal=True,
                                d=1, D=1, trace=True,
                                error_action='ignore',
                                suppress_warnings=True,
                                stepwise=True)

    hyperparams = {"Params": stepwise_model.get_params()}

    export_firebase(data=hyperparams, stock=stock, db=db, folder='SARIMAX_HYPERPARAMS', delete=True)


def predict_tomorrow_sarimax(stock, stock_data, db, params):
    """
    Hyper-parameter tuning with back-testing for SARIMAX.
    """

    history_endog = stock_data["GAIN_LOSS"]

    model = ARIMA(endog=history_endog, order=params["Params"]["order"],
                  seasonal_order=params["Params"]["seasonal_order"])
    model_fit = model.fit()
    prediction = model_fit.forecast(steps=1)
    prediction = float(prediction)

    last_date, next_date = get_dates(stock_data)

    columns = list(stock_data.columns)

    last_stats = stock_data.iloc[-1]

    data_last_stats = {}

    for entry in columns:
        data_last_stats['LAST_' + entry] = format_floats(last_stats[entry], 4)

    next_price = (1 + prediction) * float(data_last_stats["LAST_Close"])
    pred_gain_loss = format_floats(prediction, 4)
    trend_gain_loss = 'pos' if float(prediction) > 0 else 'neg'
    trend_last_gain_loss = 'pos' if float(data_last_stats["LAST_GAIN_LOSS"]) > 0 else 'neg'

    history = {
        f"{next_date}_PRED_Price": format_floats(next_price, 2),
        f"{next_date}_PRED_Price_Diff": pred_gain_loss,
        f"{next_date}_PRED_Price_Trend": trend_gain_loss,
        f"{last_date}_REAL_Price": data_last_stats["LAST_Close"],
        f"{last_date}_REAL_Price_Diff": data_last_stats["LAST_GAIN_LOSS"],
        f"{last_date}_REAL_Price_Trend": trend_last_gain_loss}

    # Export to current day folder
    export_firebase(data=history, stock=stock, db=db, folder='CURRENT_PREDS', delete=True)

    # Export to history folder
    export_firebase(data=history, stock=stock, db=db, folder='HISTORY_PREDS', delete=False)


if '__main__' == __name__:
    print('')
