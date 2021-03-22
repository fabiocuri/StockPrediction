def export_firebase(data, stock, db, folder, delete):
    """
    Exports data to Google Firebase
    """
    
    if delete:

        db.child(folder).child(stock).remove()
        
    db.child(folder).child(stock).push(data)


def retrieve_hyperparams_firebase(stock, db):
    ''' Retrieves hyper-parameters from Google Firebase for a stock already tuned '''

    users = db.child('XGBOOST_HYPERPARAMS').child(stock).get()
    params = {}

    for i in users.val():
        
        params['lstm_size'] = users.val()[i]['LSTM size']
        params['batch_size'] = users.val()[i]['Batch size']
        params['learning_rate'] = users.val()[i]['Learning rate']
        params['selected_features'] = users.val()[i]['Selected features']

    return params

def retrieve_hystoric_data(db):
    ''' Retrieves Hystoric data '''

    results = db.child('HISTORY_PREDS').get()

    return results.val()

if '__main__' == __name__:
    print('')
