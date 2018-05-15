from pandas import read_csv
from pandas import datetime
from matplotlib import pyplot
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error

def get_forecast(history, l):

    predictions = list()
    for t in range(l):
        model = ARIMA(history, order=(1,0,0))
        model_fit = model.fit(disp=0)
        output = model_fit.forecast()
        yhat = output[0]
        print ("* * * * * * * *")
        print (yhat)
        predictions.append(yhat)
        history.append(yhat)

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