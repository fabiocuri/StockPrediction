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

        params = users.val()[i]

    return params

def retrieve_hystoric_data(db):
    ''' Retrieves Hystoric data '''

    results = db.child('HISTORY_PREDS').get()

    return results.val()

if '__main__' == __name__:
    print('')
