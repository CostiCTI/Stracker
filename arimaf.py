import copy

from pandas import read_csv
from pandas import datetime
from matplotlib import pyplot
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error

def get_forecast(history, l):

    lp = [3, 4, 5, 6, 7, 8, 1, 2, 9]
    lq = [1, 0, 2, 3, 4, 5]
    ld = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    hist = copy.deepcopy(history)
    for p in lp:
        for d in ld:
            for q in lq:
                try:
                    predictions = list()
                    for t in range(l + 1):
                        model = ARIMA(history, order=(p,d,q))
                        model_fit = model.fit(disp=0)
                        output = model_fit.forecast()
                        yhat = output[0]
                        predictions.append(int(yhat))
                        history.append(int(yhat))
                    print ('* * * * * *<><><><>><>')
                    print (predictions)
                    print ('* * * * * ** * * * * * ** * * ')
                    return predictions
                except:
                    print ('EXCEPTIE')


    predictions = [0 for i in range(l + 1)]
    history = hist + predictions
    print ('* * * * * ** * * * * * ** * * ')
    print ('aici')
    print ('* * * * * ** * * * * * ** * * ')
    return predictions

#p = get_forecast([-30.0, -16.0, 18.0, 27.0, 7.0, -14.0, -22.0, -8.0, 13.0, -30.0, -16.0, 18.0, 27.0, 7.0, -14.0, -22.0, -8.0, 13.0], 5)
#print (p)

'''
error = mean_squared_error(test, predictions)
print('Test MSE: %.3f' % error)
# plot
pyplot.plot(test)
pyplot.plot(predictions, color='red')
pyplot.show()

print (l)
'''