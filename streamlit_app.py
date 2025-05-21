import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, SimpleRNN, Dense
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Load data
df = pd.read_csv("data/ultra_complex_OEE.csv")
start_date = pd.to_datetime("2020-01-01")
df['timestamp'] = start_date + pd.to_timedelta(df['hour'], unit='h')
df.set_index('timestamp', inplace=True)
df.drop(columns=['hour'], inplace=True)

# Data preprocessing
scaler = MinMaxScaler()
data = scaler.fit_transform(df['OEE'].values.reshape(-1, 1))

def create_dataset(dataset, look_back=24):
    X, Y = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        X.append(a)
        Y.append(dataset[i + look_back, 0])
    return np.array(X), np.array(Y)

look_back = 24
X, Y = create_dataset(data, look_back)
train_size = int(len(X) * 0.8)
X_train, X_test = X[0:train_size], X[train_size:len(X)]
Y_train, Y_test = Y[0:train_size], Y[train_size:len(Y)]
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# Model creation and training (example: LSTM)
lstm_model = Sequential()
lstm_model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
lstm_model.add(LSTM(units=50))
lstm_model.add(Dense(1))
lstm_model.compile(loss='mean_squared_error', optimizer='adam')
lstm_model.fit(X_train, Y_train, epochs=100, batch_size=32, verbose=0)  # verbose=0 for silent training

# Forecasting function
def forecast_future(model, last_sequence, steps_ahead=24):
    current_sequence = last_sequence.copy()
    forecasts = []
    for _ in range(steps_ahead):
        x_input = current_sequence.reshape(1, current_sequence.shape[0], 1)
        next_pred = model.predict(x_input, verbose=0)[0][0]
        forecasts.append(next_pred)
        current_sequence = np.append(current_sequence[1:], next_pred)
    return scaler.inverse_transform(np.array(forecasts).reshape(-1, 1))

# Streamlit app
st.title("Time Series OEE Forecasting")
steps_ahead = st.slider("Forecast Horizon (Hours)", min_value=1, max_value=72, value=24)

# Perform forecasting
last_known_sequence = X_test[-1]
lstm_forecast = forecast_future(lstm_model, last_known_sequence, steps_ahead=steps_ahead)

# Display results
st.header("Forecasted OEE")
st.line_chart(lstm_forecast)