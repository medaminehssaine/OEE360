import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, SimpleRNN, Dense

def load_data(file_path):
    """
    Load OEE data from CSV file and convert to time series
    
    Parameters:
    file_path: Path to the CSV file
    
    Returns:
    DataFrame with time series index
    """
    df = pd.read_csv(file_path)
    
    # Convert hour to datetime and set as index
    start_date = pd.to_datetime("2020-01-01")  # arbitrary start date
    df['timestamp'] = start_date + pd.to_timedelta(df['hour'], unit='h')
    df.set_index('timestamp', inplace=True)
    df.drop(columns=['hour'], inplace=True)
    
    return df

def plot_oee_time_series(df):
    """
    Plot OEE time series
    
    Parameters:
    df: DataFrame with OEE data
    """
    plt.figure(figsize=(14, 5))
    plt.plot(df.index, df["OEE"], color='teal')
    plt.title("OEE Over Time", fontsize=16)
    plt.xlabel("Time")
    plt.ylabel("OEE")
    plt.grid(True)
    plt.tight_layout()
    return plt

def check_stationarity(series, alpha=0.05):
    """
    Check stationarity of time series using ADF, KPSS, and PP tests
    
    Parameters:
    series: Time series to check
    alpha: Significance level
    
    Returns:
    Dictionary with test results
    """
    # ADF test
    result_adf = adfuller(series.dropna())
    adf_stationary = result_adf[1] < alpha
    
    # KPSS test
    result_kpss = kpss(series.dropna())
    kpss_stationary = result_kpss[1] > alpha
    
    return {
        'adf_statistic': result_adf[0],
        'adf_pvalue': result_adf[1],
        'adf_critical_values': result_adf[4],
        'adf_stationary': adf_stationary,
        'kpss_statistic': result_kpss[0],
        'kpss_pvalue': result_kpss[1],
        'kpss_critical_values': result_kpss[3],
        'kpss_stationary': kpss_stationary,
        'overall_stationary': adf_stationary and kpss_stationary
    }

def plot_acf_pacf(series, lags=48):
    """
    Plot ACF and PACF for time series
    
    Parameters:
    series: Time series to plot
    lags: Number of lags to include
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    plot_acf(series.dropna(), ax=axes[0], lags=lags)
    axes[0].set_title('ACF')
    
    plot_pacf(series.dropna(), ax=axes[1], lags=lags, method='ywm')
    axes[1].set_title('PACF')
    
    plt.tight_layout()
    return plt

def create_dataset(dataset, look_back=24):
    """
    Create dataset for time series forecasting
    
    Parameters:
    dataset: Dataset to use
    look_back: Number of previous time steps to use as input
    
    Returns:
    X, Y arrays for model training
    """
    X, Y = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        X.append(a)
        Y.append(dataset[i + look_back, 0])
    return np.array(X), np.array(Y)

def build_model(model_type, input_shape):
    """
    Build time series forecasting model
    
    Parameters:
    model_type: Type of model to build (RNN, LSTM, or GRU)
    input_shape: Shape of input data
    
    Returns:
    Compiled Keras model
    """
    model = Sequential()
    
    if model_type == 'RNN':
        model.add(SimpleRNN(units=50, return_sequences=True, input_shape=input_shape))
        model.add(SimpleRNN(units=50))
    elif model_type == 'LSTM':
        model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
        model.add(LSTM(units=50))
    elif model_type == 'GRU':
        model.add(GRU(units=50, return_sequences=True, input_shape=input_shape))
        model.add(GRU(units=50))
    
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    
    return model

def forecast_future(model, last_sequence, steps_ahead, scaler):
    """
    Generate forecasts for future time steps
    
    Parameters:
    model: Trained Keras model
    last_sequence: Last known sequence of values
    steps_ahead: Number of steps to forecast
    scaler: Scaler used to normalize data
    
    Returns:
    Array of forecasted values
    """
    current_sequence = last_sequence.copy()
    forecasts = []
    
    for _ in range(steps_ahead):
        x_input = current_sequence.reshape(1, current_sequence.shape[0], 1)
        next_pred = model.predict(x_input, verbose=0)[0][0]
        forecasts.append(next_pred)
        current_sequence = np.append(current_sequence[1:], next_pred)
    
    return scaler.inverse_transform(np.array(forecasts).reshape(-1, 1))