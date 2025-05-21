import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import tensorflow as tf
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import LSTM, GRU, SimpleRNN, Dense
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import io
import base64
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="OEE Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply dark theme with custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stSidebar {
        background-color: #252526;
    }
    .css-145kmo2 {
        color: #FFFFFF;
    }
    .stSelectbox label, .stSlider label {
        color: #FFFFFF;
    }
    .stMarkdown {
        color: #FFFFFF;
    }
    .custom-metric-container {
        background-color: #252526;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .css-1kyxreq {
        background-color: #333333;
    }
    button {
        background-color: #0078D4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🏭 OEE Analytics Dashboard")
st.markdown("### Overall Equipment Effectiveness Analysis & Forecasting")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/ultra_complex_OEE.csv")
        # Convert hour to datetime and set as index
        start_date = pd.to_datetime("2020-01-01")  # arbitrary start date
        df['timestamp'] = start_date + pd.to_timedelta(df['hour'], unit='h')
        df.set_index('timestamp', inplace=True)
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'ultra_complex_OEE.csv' is in the correct location.")
        return None

df = load_data()

if df is not None:
    # Sidebar
    st.sidebar.title("Dashboard Controls")

    # Date range selector
    st.sidebar.subheader("Time Period Selection")
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [df.index.min().date(), df.index.max().date()],
        min_value=df.index.min().date(),
        max_value=df.index.max().date()
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        filtered_df = df[(df.index >= start_date) & (df.index <= end_date)]
    else:
        filtered_df = df.copy()

    # Visualization options
    st.sidebar.subheader("Visualization Options")
    chart_type = st.sidebar.selectbox(
        "Select Chart Type",
        ["Line Chart", "Area Chart", "Bar Chart", "Heatmap", "3D Scatter"]
    )

    variables = st.sidebar.multiselect(
        "Select Variables for Analysis",
        options=df.columns.tolist(),
        default=["OEE", "availability", "performance", "quality"]
    )

    # Model selection for forecasting
    st.sidebar.subheader("Forecasting Options")
    model_type = st.sidebar.selectbox(
        "Select Model Type for Forecasting",
        ["RNN", "LSTM", "GRU"]
    )

    forecast_horizon = st.sidebar.slider("Forecast Horizon (hours)", 1, 168, 24)
    lookback_window = st.sidebar.slider("Lookback Window (hours)", 1, 168, 24)

    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Average OEE", f"{filtered_df['OEE'].mean():.2%}", f"{filtered_df['OEE'].mean() - df['OEE'].mean():.2%}")
    with col2:
        st.metric("Availability", f"{filtered_df['availability'].mean():.2%}", f"{filtered_df['availability'].mean() - df['availability'].mean():.2%}")
    with col3:
        st.metric("Performance", f"{filtered_df['performance'].mean():.2%}", f"{filtered_df['performance'].mean() - df['performance'].mean():.2%}")
    with col4:
        st.metric("Quality", f"{filtered_df['quality'].mean():.2%}", f"{filtered_df['quality'].mean() - df['quality'].mean():.2%}")

    # Time series visualization
    st.header("OEE Time Series Analysis")

    tab1, tab2, tab3, tab4 = st.tabs(["Time Series", "Correlation Analysis", "Statistical Tests", "Forecasting"])

    with tab1:
        st.subheader("Time Series Visualization")

        if chart_type == "Line Chart":
            fig = px.line(filtered_df, y=variables, title="OEE Components Over Time")
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor='rgba(30, 30, 30, 0.8)',
                paper_bgcolor='rgba(30, 30, 30, 0.8)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Area Chart":
            fig = px.area(filtered_df, y=variables, title="OEE Components Over Time")
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor='rgba(30, 30, 30, 0.8)',
                paper_bgcolor='rgba(30, 30, 30, 0.8)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Bar Chart":
            daily_data = filtered_df.resample('D').mean()
            fig = px.bar(daily_data, y=variables, title="Daily Average OEE Components")
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor='rgba(30, 30, 30, 0.8)',
                paper_bgcolor='rgba(30, 30, 30, 0.8)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Heatmap":
            if len(variables) > 0:
                hourly_data = filtered_df[variables].groupby(filtered_df.index.hour).mean()
                daily_data = filtered_df[variables].groupby(filtered_df.index.dayofweek).mean()

                col1, col2 = st.columns(2)

                with col1:
                    fig = px.imshow(
                        hourly_data.T,
                        title="Hourly Heatmap",
                        labels=dict(x="Hour of Day", y="Metric", color="Value"),
                        x=hourly_data.index,
                        y=hourly_data.columns,
                        color_continuous_scale="Viridis"
                    )
                    fig.update_layout(template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    fig = px.imshow(
                        daily_data.T,
                        title="Day of Week Heatmap",
                        labels=dict(x="Day of Week", y="Metric", color="Value"),
                        x=days,
                        y=daily_data.columns,
                        color_continuous_scale="Viridis"
                    )
                    fig.update_layout(template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "3D Scatter":
            if len(variables) >= 3:
                fig = px.scatter_3d(
                    filtered_df,
                    x=variables[0],
                    y=variables[1],
                    z=variables[2],
                    color="OEE" if "OEE" in filtered_df.columns else None,
                    title="3D Relationship Between Variables"
                )
                fig.update_layout(
                    template="plotly_dark",
                    scene=dict(
                        xaxis_title=variables[0],
                        yaxis_title=variables[1],
                        zaxis_title=variables[2]
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Please select at least 3 variables for 3D visualization")

        # Seasonal decomposition
        if st.checkbox("Show Seasonal Decomposition"):
            target_var = st.selectbox("Select variable for decomposition", variables)

            try:
                decomposition = seasonal_decompose(filtered_df[target_var], model='additive', period=24)

                fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                                   subplot_titles=("Original", "Trend", "Seasonal", "Residual"))

                fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df[target_var], name="Original"), row=1, col=1)
                fig.add_trace(go.Scatter(x=filtered_df.index, y=decomposition.trend, name="Trend"), row=2, col=1)
                fig.add_trace(go.Scatter(x=filtered_df.index, y=decomposition.seasonal, name="Seasonal"), row=3, col=1)
                fig.add_trace(go.Scatter(x=filtered_df.index, y=decomposition.resid, name="Residual"), row=4, col=1)

                fig.update_layout(height=800, title_text=f"Seasonal Decomposition of {target_var}", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error performing decomposition: {e}")

    with tab2:
        st.subheader("Correlation Analysis")

        corr_vars = st.multiselect(
            "Select Variables for Correlation Analysis",
            options=df.columns.tolist(),
            default=["OEE", "availability", "performance", "quality", "energy_price", "temp", "humidity"]
        )

        if corr_vars:
            corr_matrix = filtered_df[corr_vars].corr()

            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                color_continuous_scale="RdBu_r",
                title="Correlation Matrix",
                zmin=-1, zmax=1
            )
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            # Scatter plot matrix
            if st.checkbox("Show Scatter Plot Matrix"):
                if len(corr_vars) <= 6:  # Limit to 6 variables to avoid overcrowding
                    fig = px.scatter_matrix(
                        filtered_df[corr_vars],
                        dimensions=corr_vars,
                        color="OEE" if "OEE" in corr_vars else None,
                        title="Scatter Plot Matrix"
                    )
                    fig.update_layout(template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Please select 6 or fewer variables for the scatter plot matrix")
        else:
            st.info("Please select variables for correlation analysis")

    with tab3:
        st.subheader("Statistical Tests")
        test_var = st.selectbox("Select Variable for Statistical Tests", variables)

        col1, col2 = st.columns(2)

        with col1:
            # ACF plot
            fig, ax = plt.subplots(figsize=(10, 4))
            plt.style.use('dark_background')
            plot_acf(filtered_df[test_var].dropna(), ax=ax, lags=48)
            ax.set_title(f'ACF - {test_var}', color='white')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.grid(True, linestyle='--', alpha=0.7)
            st.pyplot(fig)

        with col2:
            # PACF plot
            fig, ax = plt.subplots(figsize=(10, 4))
            plt.style.use('dark_background')
            plot_pacf(filtered_df[test_var].dropna(), ax=ax, lags=48, method='ywm')
            ax.set_title(f'PACF - {test_var}', color='white')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.grid(True, linestyle='--', alpha=0.7)
            st.pyplot(fig)

        # Stationarity Tests
        if st.checkbox("Run Stationarity Tests"):
            alpha = 0.05

            # ADF Test
            try:
                result_adf = adfuller(filtered_df[test_var].dropna())
                adf_stationary = result_adf[1] < alpha

                # KPSS Test
                result_kpss = kpss(filtered_df[test_var].dropna())
                kpss_stationary = result_kpss[1] > alpha

                # Results display
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### ADF Test Results")
                    st.markdown(f"**ADF Statistic:** {result_adf[0]:.4f}")
                    st.markdown(f"**p-value:** {result_adf[1]:.4f}")
                    st.markdown("**Critical Values:**")
                    for key, value in result_adf[4].items():
                        st.markdown(f"- {key}: {value:.4f}")
                    st.markdown(f"**Is Stationary:** {'✅ Yes' if adf_stationary else '❌ No'}")

                with col2:
                    st.markdown("#### KPSS Test Results")
                    st.markdown(f"**KPSS Statistic:** {result_kpss[0]:.4f}")
                    st.markdown(f"**p-value:** {result_kpss[1]:.4f}")
                    st.markdown("**Critical Values:**")
                    for key, value in result_kpss[3].items():
                        st.markdown(f"- {key}: {value:.4f}")
                    st.markdown(f"**Is Stationary:** {'✅ Yes' if kpss_stationary else '❌ No'}")

                # Differencing if needed
                if not (adf_stationary and kpss_stationary):
                    if st.checkbox("Apply Differencing"):
                        diff_df = filtered_df[test_var].diff().dropna()

                        # Test differenced series
                        diff_adf = adfuller(diff_df)
                        diff_kpss = kpss(diff_df)

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=diff_df.index, y=diff_df, mode='lines', name='Differenced Series'))
                        fig.update_layout(
                            title=f"Differenced {test_var}",
                            template="plotly_dark"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        st.markdown("#### Stationarity Tests on Differenced Series")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**ADF p-value:** {diff_adf[1]:.4f} - {'✅ Stationary' if diff_adf[1] < alpha else '❌ Non-stationary'}")
                        with col2:
                            st.markdown(f"**KPSS p-value:** {diff_kpss[1]:.4f} - {'✅ Stationary' if diff_kpss[1] > alpha else '❌ Non-stationary'}")

            except Exception as e:
                st.error(f"Error running stationarity tests: {e}")

    with tab4:
        st.subheader("OEE Forecasting")

        forecast_variable = st.selectbox("Select Variable to Forecast", variables, index=variables.index("OEE") if "OEE" in variables else 0)

        # Helper function to create dataset for time series models
        @st.cache_resource
        def create_dataset(data, look_back):
            X, Y = [], []
            for i in range(len(data) - look_back - 1):
                X.append(data[i:(i+look_back)])
                Y.append(data[i + look_back])
            return np.array(X), np.array(Y)

        # Train model function
        def train_model(model_type, X_train, Y_train):
            model = Sequential()

            if model_type == "RNN":
                model.add(SimpleRNN(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
                model.add(SimpleRNN(units=50))
            elif model_type == "LSTM":
                model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
                model.add(LSTM(units=50))
            elif model_type == "GRU":
                model.add(GRU(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
                model.add(GRU(units=50))

            model.add(Dense(1))
            model.compile(loss='mean_squared_error', optimizer='adam')

            model.fit(X_train, Y_train, epochs=50, batch_size=32, verbose=0)
            return model

        # Forecast function
        def forecast_future(model, last_sequence, steps_ahead, scaler):
            current_sequence = last_sequence.copy()
            forecasts = []

            for _ in range(steps_ahead):
                x_input = current_sequence.reshape(1, current_sequence.shape[0], 1)
                next_pred = model.predict(x_input, verbose=0)[0][0]
                forecasts.append(next_pred)
                current_sequence = np.append(current_sequence[1:], next_pred)

            return scaler.inverse_transform(np.array(forecasts).reshape(-1, 1))

        if st.button("Generate Forecast"):
            with st.spinner(f"Training {model_type} model and generating forecast..."):
                try:
                    # Prepare data
                    data_to_forecast = filtered_df[forecast_variable].values.reshape(-1, 1)
                    scaler = MinMaxScaler()
                    scaled_data = scaler.fit_transform(data_to_forecast)

                    X, Y = create_dataset(scaled_data, lookback_window)

                    train_size = int(len(X) * 0.8)
                    X_train, X_test = X[0:train_size], X[train_size:len(X)]
                    Y_train, Y_test = Y[0:train_size], Y[train_size:len(Y)]

                    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
                    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

                    # Train model
                    model = train_model(model_type, X_train, Y_train)

                    # Make predictions for test data
                    test_predictions = model.predict(X_test)
                    test_predictions = scaler.inverse_transform(test_predictions)
                    Y_test_inv = scaler.inverse_transform(Y_test.reshape(-1, 1))

                    # Generate future forecasts
                    last_sequence = scaled_data[-lookback_window:]
                    forecast = forecast_future(model, last_sequence, forecast_horizon, scaler)

                    # Create time indices for plotting
                    last_date = filtered_df.index[-1]
                    future_dates = [last_date + timedelta(hours=i+1) for i in range(forecast_horizon)]

                    # Plot results
                    fig = go.Figure()

                    # Historical data
                    fig.add_trace(go.Scatter(
                        x=filtered_df.index[-100:],
                        y=filtered_df[forecast_variable].values[-100:],
                        mode='lines',
                        name='Historical Data',
                        line=dict(color='blue')
                    ))

                    # Forecast
                    fig.add_trace(go.Scatter(
                        x=future_dates,
                        y=forecast.flatten(),
                        mode='lines',
                        name='Forecast',
                        line=dict(color='red')
                    ))

                    # Add confidence interval (simple approach)
                    error = np.std(Y_test_inv - test_predictions)
                    fig.add_trace(go.Scatter(
                        x=future_dates + future_dates[::-1],
                        y=np.concatenate([forecast.flatten() + 2*error, (forecast.flatten() - 2*error)[::-1]]),
                        fill='toself',
                        fillcolor='rgba(255,0,0,0.2)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='95% Confidence Interval'
                    ))

                    # Add vertical line at current time
                    fig.add_vline(x=last_date, line_width=2, line_dash="dash", line_color="white")
                    fig.add_annotation(x=last_date, y=max(filtered_df[forecast_variable].values[-30:]),
                                    text="Current Time", showarrow=True, arrowhead=1, ax=40)

                    fig.update_layout(
                        title=f"{forecast_horizon}-hour Forecast of {forecast_variable} using {model_type}",
                        xaxis_title="Time",
                        yaxis_title=forecast_variable,
                        template="plotly_dark",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Display forecast stats
                    st.markdown("### Forecast Statistics")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Min Forecast", f"{np.min(forecast):.4f}")
                    with col2:
                        st.metric("Max Forecast", f"{np.max(forecast):.4f}")
                    with col3:
                        st.metric("Mean Forecast", f"{np.mean(forecast):.4f}")
                    with col4:
                        st.metric("Forecast Trend",
                                f"{(forecast[-1][0] - forecast[0][0]):.4f}",
                                f"{((forecast[-1][0] - forecast[0][0])/forecast[0][0]*100):.2f}%")

                    # Export forecast
                    forecast_df = pd.DataFrame({
                        'Timestamp': future_dates,
                        'Forecast': forecast.flatten(),
                        'Upper_Bound': forecast.flatten() + 2*error,
                        'Lower_Bound': forecast.flatten() - 2*error
                    })

                    csv = forecast_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="oee_forecast.csv">Download Forecast CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error generating forecast: {e}")

    # Additional dashboard components
    st.header("OEE Breakdown Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # OEE by shift
        shift_data = filtered_df.groupby('shift')['OEE'].mean().reset_index()
        fig = px.bar(
            shift_data,
            x="shift",
            y="OEE",
            title="Average OEE by Shift",
            labels={"shift": "Shift", "OEE": "Average OEE"},
            color="OEE",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Downtime analysis
        downtime_hours = filtered_df[filtered_df['downtime'] > 0].resample('D').count()['downtime']
        fig = px.line(
            x=downtime_hours.index,
            y=downtime_hours.values,
            title="Daily Downtime Events",
            labels={"x": "Date", "y": "Number of Hours with Downtime"}
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # Relationship analysis
    st.header("Factor Impact Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Temperature vs OEE
        fig = px.scatter(
            filtered_df,
            x="temp",
            y="OEE",
            title="Temperature vs OEE",
            trendline="ols",
            color="shift",
            labels={"temp": "Temperature", "OEE": "OEE Value"}
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Worker fatigue vs OEE
        fig = px.scatter(
            filtered_df,
            x="fatigue",
            y="OEE",
            title="Worker Fatigue vs OEE",
            trendline="ols",
            color="shift",
            labels={"fatigue": "Worker Fatigue", "OEE": "OEE Value"}
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # Footer with information
    st.markdown("---")
    st.markdown("### About This Dashboard")
    st.markdown("""
    This interactive dashboard provides comprehensive analysis of Overall Equipment Effectiveness (OEE) data.
    It includes time series analysis, correlations, forecasting capabilities, and factor impact analysis.

    - Use the date range selector to filter data
    - Explore different visualization options
    - Generate forecasts with different models and parameters
    - Analyze the factors that impact OEE the most

    Data is refreshed automatically when the dashboard is loaded.
    """)

    # Add download links for raw data
    if st.checkbox("Show Raw Data"):
        st.dataframe(filtered_df)

        csv = filtered_df.to_csv(index=True)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="filtered_oee_data.csv">Download Filtered Data as CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
else:
    st.error("Unable to load data. Please check if the data file is available.")