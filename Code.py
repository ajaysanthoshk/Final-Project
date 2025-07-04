
"""Importing Libraries"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Plotly for interactive charts
!pip install keras-tuner shap --quiet
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Conv1D, Flatten
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy.stats import norm, ttest_rel
import keras_tuner as kt
import shap
import plotly.express as px
import plotly.graph_objs as go

try:
    import gdown
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "--upgrade", "gdown"])
    import gdown

file_id = "16roDpQxTS2s-X7Lxg8wwEaoZ89k16I6V"
output_path = os.path.join("data", "all_stocks_5yr.csv")
os.makedirs("data", exist_ok=True)

if not os.path.exists(output_path):
    print("⬇️ Downloading dataset...")
    gdown.download(id=file_id, output=output_path, quiet=False)
else:
    print("✅ Dataset already exists.")

"""Data Cleaning process"""

data = pd.read_csv(output_path)
data['date'] = pd.to_datetime(data['date'])
data.sort_values(['Name', 'date'], inplace=True)
data.reset_index(drop=True, inplace=True)

print(data.shape)
print(data.columns)
print(data['Name'].nunique())  # Number of unique stocks
data.isnull().sum()

df = pd.DataFrame(data)

print("Original DataFrame:")
print(df)
stock_names=df['Name'].unique()
print(stock_names)

# Fill missing values with the mean of specific columns: 'open', 'high', and 'low'
columns_to_fill = ['open', 'high', 'low']
df[columns_to_fill] = df[columns_to_fill].fillna(df[columns_to_fill].mean())

print("\nDataFrame after filling missing values with the average in specified columns:")
print(df)

df.isnull().sum()

"""Exploratory Data Analysis"""

# Check Summary Statistics
df.describe()

# Plot closing prices of major stocks
companies = ['AAPL', 'GOOGL', 'AMZN', 'MSFT']

plt.figure(figsize=(16, 8))
for company in companies:
    stock = df[df['Name'] == company]
    plt.plot(stock['date'], stock['close'], label=company)

plt.legend()
plt.title('Stock Closing Prices Over Time')
plt.xlabel('Date')
plt.ylabel('Closing Price')
plt.grid()
plt.show()

# Distribution of Daily Returns for a Stock
stock = df[df['Name'] == 'AAPL'].copy()
stock['daily_return'] = stock['close'].pct_change()

plt.figure(figsize=(10, 5))
sns.histplot(stock['daily_return'].dropna(), bins=100, kde=True)
plt.title('Distribution of Daily Returns - AAPL')
plt.xlabel('Daily Return')
plt.show()

# Volatility Comparison (Rolling Standard Deviation)
plt.figure(figsize=(14, 6))
for company in ['AAPL', 'GOOG', 'AMZN']:
    subset = df[df['Name'] == company].copy()
    subset.set_index('date', inplace=True)
    subset['rolling_vol'] = subset['close'].pct_change().rolling(window=30).std()
    plt.plot(subset['rolling_vol'], label=company)

plt.title('30-Day Rolling Volatility')
plt.ylabel('Volatility')
plt.xlabel('Date')
plt.legend()
plt.grid()
plt.show()

# Moving Averages
apple = df[df['Name'] == 'AAPL'].copy()
apple.set_index('date', inplace=True)
apple['MA50'] = apple['close'].rolling(window=50).mean()
apple['MA200'] = apple['close'].rolling(window=200).mean()

plt.figure(figsize=(14, 6))
plt.plot(apple['close'], label='Close Price')
plt.plot(apple['MA50'], label='50-Day MA')
plt.plot(apple['MA200'], label='200-Day MA')
plt.title('AAPL - Moving Averages')
plt.legend()
plt.grid()
plt.show()

# Correlation Matrix of Closing Prices (Top 20 Stocks)
top20 = df['Name'].value_counts().head(20).index.tolist()
filtered_df = df[df['Name'].isin(top20)]
pivot = filtered_df.pivot(index='date', columns='Name', values='close')
correlation_matrix = pivot.corr()
plt.figure(figsize=(14, 12))
sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', center=0)
plt.title("Correlation Matrix of Top 20 Stocks")
plt.show()

# Stock Price Distribution Using KDE (Kernel Density Estimation)
plt.figure(figsize=(12, 6))
for stock in ['AAPL', 'GOOGL', 'AMZN', 'MSFT']:
    sns.kdeplot(df[df['Name'] == stock]['close'], label=stock, fill=True)

plt.title("Stock Price Distributions")
plt.xlabel("Closing Price")
plt.legend()
plt.show()

# Rolling Mean (Moving Average) Analysis
apple = df[df['Name'] == 'AAPL'].copy()
apple['MA50'] = apple['close'].rolling(window=50).mean()
apple['MA200'] = apple['close'].rolling(window=200).mean()
plt.figure(figsize=(14, 7))
plt.plot(apple['date'], apple['close'], label="Close Price", alpha=0.7)
plt.plot(apple['date'], apple['MA50'], label="50-Day MA", linestyle='dashed')
plt.plot(apple['date'], apple['MA200'], label="200-Day MA", linestyle='dashed')

plt.legend()
plt.title("AAPL - Moving Averages (50-day & 200-day)")
plt.show()

# Boxplot for Stock Price Distribution
plt.figure(figsize=(12, 6))
sns.boxplot(x='Name', y='close', data=df[df['Name'].isin(['AAPL', 'GOOGL', 'AMZN', 'MSFT'])])
plt.xticks(rotation=45)
plt.title('Stock Price Distribution (Boxplot)')
plt.show()

# Pairplot for Selected Stocks
selected_stocks = df[df['Name'].isin(['AAPL', 'GOOGL', 'AMZN', 'MSFT'])]
pivoted = selected_stocks.pivot(index='date', columns='Name', values='close')
sns.pairplot(pivoted)
plt.show()

# Candlestick Chart for AAPL
fig = go.Figure(data=[go.Candlestick(x=apple['date'],
                open=apple['open'],
                high=apple['high'],
                low=apple['low'],
                close=apple['close'])])
fig.update_layout(title='AAPL Candlestick Chart', xaxis_rangeslider_visible=False)
fig.show()

# Bollinger Bands for AAPL
apple['SMA20'] = apple['close'].rolling(window=20).mean()
apple['UpperBand'] = apple['SMA20'] + 2 * apple['close'].rolling(window=20).std()
apple['LowerBand'] = apple['SMA20'] - 2 * apple['close'].rolling(window=20).std()

plt.figure(figsize=(14, 7))
plt.plot(apple['date'], apple['close'], label='Close Price', alpha=0.7)
plt.plot(apple['date'], apple['SMA20'], label='20-Day SMA', linestyle='dashed')
plt.fill_between(apple['date'], apple['UpperBand'], apple['LowerBand'], color='gray', alpha=0.3)

plt.legend()
plt.title('AAPL - Bollinger Bands')
plt.show()

# Daily Return Percentage for Selected Stocks
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 10))

company_list = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
for i, stock in enumerate(company_list):
    df_stock = df[df['Name'] == stock].copy()
    df_stock['Daily Return'] = df_stock['close'].pct_change()

    row, col = divmod(i, 2)
    df_stock['Daily Return'].plot(ax=axes[row, col], legend=True, linestyle='--', marker='o')
    axes[row, col].set_title(stock)

fig.tight_layout()
plt.show()

# Increase figure size
plt.figure(figsize=(15, 8))
# Convert columns to numeric, forcing errors to NaN
df_numeric = df.apply(pd.to_numeric, errors='coerce')

# Compute correlation, filling NaN values with 0
correlation_matrix = df_numeric.corr().fillna(0)

# Create heatmap with optimized settings
sns.heatmap(correlation_matrix, annot=False, cmap="coolwarm", linewidths=0.5)

plt.title("Stock Closing Price Correlation")
plt.xticks(rotation=90)  # Rotate x-axis labels for readability
plt.yticks(rotation=0)
plt.show()

plt.figure(figsize=(12, 6))

for stock in company_list:
    daily_returns = df[df['Name'] == stock]['close'].pct_change().dropna()
    plt.hist(daily_returns, bins=50, alpha=0.7, label=stock)

plt.legend()
plt.xlabel('Daily Return')
plt.ylabel('Frequency')
plt.title("Histogram of Daily Returns")
plt.show()

plt.figure(figsize=(14, 6))

for stock in company_list:
    subset = df[df['Name'] == stock]
    plt.plot(subset['date'], subset['high'], label=f'{stock} High', alpha=0.6)
    plt.plot(subset['date'], subset['low'], label=f'{stock} Low', alpha=0.6)

plt.legend()
plt.title('High & Low Prices Over Time')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

df_filtered = df[(df['date'] >= '2017-01-01') & (df['date'] <= '2018-12-31')]

plt.figure(figsize=(12, 6))
for stock in company_list:
    subset = df_filtered[df_filtered['Name'] == stock]
    plt.plot(subset['date'], subset['close'], label=f'{stock} Close')

plt.legend()
plt.title("Stock's Prices from 2017 to 2018")
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.xticks(rotation=45)
plt.show()

df_jan2018 = df[(df['date'] >= '2018-01-01') & (df['date'] <= '2018-01-31')]

plt.figure(figsize=(12, 6))
for stock in company_list:
    subset = df_jan2018[df_jan2018['Name'] == stock]
    plt.plot(subset['date'], subset['close'], label=f'{stock} Close', linestyle='solid')
    plt.plot(subset['date'], subset['high'], label=f'{stock} High', linestyle='dashed')
    plt.plot(subset['date'], subset['low'], label=f'{stock} Low', linestyle='dotted')

plt.legend()
plt.title("Stock Prices in January 2018")
plt.xlabel("Date")
plt.ylabel("Price")
plt.xticks(rotation=45)
plt.show()

df_volume = df.groupby('Name')['volume'].sum().nlargest(10)

plt.figure(figsize=(8, 8))
plt.pie(df_volume, labels=df_volume.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
plt.title('Total Trading Volume by Company')
plt.show()

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Example placeholder for compute_rsi
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / (avg_loss + 1e-8)
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Example placeholder for create_sequences
def create_sequences(data, time_steps=50):
    X = []
    y = []
    for i in range(len(data) - time_steps):
        X.append(data[i:i+time_steps])
        y.append(data[i+time_steps, 0])  # Assuming 'close' is at index 0
    return np.array(X), np.array(y).reshape(-1, 1)

# Example DataFrame setup (simulate some data):

np.random.seed(42)
num_samples = 1000
stock_names = ['AAPL', 'GOOG']
data_records = []

for name in stock_names:
    close_prices = np.cumsum(np.random.randn(num_samples)) + 100
    for i in range(num_samples):
        data_records.append({
            'Name': name,
            'close': close_prices[i],
            'date': pd.Timestamp('2020-01-01') + pd.Timedelta(days=i)
        })

data = pd.DataFrame(data_records)

# 1. Feature Engineering
data['RSI'] = compute_rsi(data['close'])
data['MA_7'] = data['close'].rolling(7).mean()
data['MA_30'] = data['close'].rolling(30).mean()
data['Volatility'] = data['close'].rolling(7).std()
data.dropna(inplace=True)

# 2. Scale entire dataset
scaler = MinMaxScaler()
scaled_features = ['close', 'MA_7', 'MA_30', 'Volatility', 'RSI']
scaled_data = scaler.fit_transform(data[scaled_features])

# 3. Create sequences for the entire dataset (optional)
X_all, y_all = create_sequences(scaled_data, time_steps=50)

# 4. Split into train/test for the entire dataset
split_idx = int(0.8 * len(X_all))
X_train, X_test = X_all[:split_idx], X_all[split_idx:]
y_train, y_test = y_all[:split_idx], y_all[split_idx:]

# 5. Loop through each stock to evaluate
for stock in stock_names:
    # Filter data for the current stock
    stock_df = data[data['Name'] == stock].copy()
    stock_scaled = scaler.transform(stock_df[scaled_features])

    # Create sequences for this stock
    X_stock, y_stock = create_sequences(stock_scaled, time_steps=50)

    # Split stock data into train/test
    split_idx_stock = int(0.8 * len(X_stock))
    X_train_stock = X_stock[:split_idx_stock]
    y_train_stock = y_stock[:split_idx_stock]
    X_test_stock = X_stock[split_idx_stock:]
    y_test_stock = y_stock[split_idx_stock:]

    # --- Naive Persistence Baseline ---
    # Prediction is the last 'close' value in each sequence
    last_close_vals = X_test_stock[:, -1, 0]  # 'close' is at index 0
    y_pred_naive = last_close_vals.reshape(-1, 1)

    # Evaluation of naive baseline
    mse_naive = mean_squared_error(y_test_stock, y_pred_naive)
    mae_naive = mean_absolute_error(y_test_stock, y_pred_naive)

    print(f"Naive baseline for {stock}: MSE={mse_naive:.4f}, MAE={mae_naive:.4f}")

y_pred_model = np.zeros_like(y_test_stock)

# Evaluate your model
 mse_model =mean_squared_error(y_test_stock, y_pred_model)
 mae_model =mean_absolute_error(y_test_stock, y_pred_model)

print(f"Model performance for {stock}:MSE={mse_model:.4f},MAE={mae_model:.4f}")
print('-' * 50)

# Early stopping
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Build models (LSTM, GRU, CNN) with hyperparameter tuning
def build_lstm_model(hp):
    model = Sequential()
    for i in range(hp.Int('num_layers', 1, 2)):
        model.add(LSTM(
            units=hp.Int(f'units_{i}', 32, 128, step=32),
            return_sequences=(i < 1),
            input_shape=(X_train.shape[1], X_train.shape[2]),
            recurrent_activation='sigmoid'  # disables CuDNNRNN for compatibility
        ))
        model.add(Dropout(hp.Float(f'dropout_{i}', 0.2, 0.5, step=0.1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model

def build_gru_model(hp):
    model = Sequential()
    for i in range(hp.Int('num_layers', 1, 2)):
        model.add(GRU(
            units=hp.Int(f'units_{i}', 32, 128, step=32),
            return_sequences=(i < 1),
            input_shape=(X_train.shape[1], X_train.shape[2]),
            recurrent_activation='sigmoid'  # disables CuDNNRNN
        ))
        model.add(Dropout(hp.Float(f'dropout_{i}', 0.2, 0.5, step=0.1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model

# Tuning with RandomSearch (faster, more control)
tuner_lstm = kt.RandomSearch(build_lstm_model, objective='val_loss', max_trials=10, executions_per_trial=1, directory='lstm_tuner', project_name='lstm')
tuner_gru = kt.RandomSearch(build_gru_model, objective='val_loss', max_trials=10, executions_per_trial=1, directory='gru_tuner', project_name='gru')

X_val = X_test[:len(X_test)//2]
y_val = y_test[:len(y_test)//2]

tuner_lstm.search(X_train, y_train, validation_data=(X_val, y_val), callbacks=[early_stop])

tuner_gru.search(X_train, y_train, validation_data=(X_val, y_val), callbacks=[early_stop])

best_lstm = tuner_lstm.get_best_models(1)[0]
best_lstm.compile(optimizer='adam', loss='mse')

best_gru = tuner_gru.get_best_models(1)[0]
best_gru.compile(optimizer='adam', loss='mse')

# CNN
model_cnn = Sequential([
    Conv1D(64, 3, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])),
    Dropout(0.3),
    Flatten(),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(1)
])
model_cnn.compile(optimizer='adam', loss='mse')

# Train models (use high epochs for better training)
EPOCHS = 30
history_lstm = best_lstm.fit(X_train, y_train, epochs=EPOCHS, batch_size=32,
                             validation_data=(X_test, y_test), callbacks=[early_stop], verbose=1)
history_gru = best_gru.fit(X_train, y_train, epochs=EPOCHS, batch_size=32,
                           validation_data=(X_test, y_test), callbacks=[early_stop], verbose=1)
history_cnn = model_cnn.fit(X_train, y_train, epochs=EPOCHS, batch_size=32,
                            validation_data=(X_test, y_test), callbacks=[early_stop], verbose=1)

# Predictions
pred_lstm = best_lstm.predict(X_test)
pred_gru = best_gru.predict(X_test)
pred_cnn = model_cnn.predict(X_test)
ensemble_pred = (pred_lstm + pred_gru + pred_cnn) / 3

# Inverse scaling predictions
def inverse_preds(preds):
    return scaler.inverse_transform(np.hstack((preds, np.zeros((len(preds), 4)))) )[:, 0]

# Actual prices
y_test_actual = inverse_preds(y_test.reshape(-1, 1))
# Predictions
pred_lstm_actual = inverse_preds(pred_lstm)
pred_gru_actual = inverse_preds(pred_gru)
pred_cnn_actual = inverse_preds(pred_cnn)
ensemble_actual = inverse_preds(ensemble_pred)

# Evaluation
def print_metrics(true, pred, name):
    print(f"{name} -- RMSE: {np.sqrt(mean_squared_error(true, pred)):.2f}, MAE: {mean_absolute_error(true, pred):.2f}, R2: {r2_score(true, pred):.2f}")

print_metrics(y_test_actual, pred_lstm_actual, "LSTM")
print_metrics(y_test_actual, pred_gru_actual, "GRU")
print_metrics(y_test_actual, pred_cnn_actual, "CNN")
print_metrics(y_test_actual, ensemble_actual, "Ensemble")

# Confidence intervals (uncertainty)
def get_ci(preds):
    preds_array = np.array([preds for _ in range(100)])
    mean = preds_array.mean(axis=0)
    std = preds_array.std(axis=0)
    z = norm.ppf(0.975)
    lower = mean - z * std
    upper = mean + z * std
    return inverse_preds(mean), inverse_preds(lower), inverse_preds(upper)

ensemble_mean, ensemble_low, ensemble_high = get_ci(ensemble_pred)

# Plot predictions with confidence intervals
plt.figure(figsize=(14,6))
plt.plot(y_test_actual, label='Actual', color='black')
plt.plot(ensemble_mean, label='Predicted', color='blue')
plt.fill_between(range(len(ensemble_mean)), ensemble_low, ensemble_high, alpha=0.3, label='95% CI')
plt.legend()
plt.title("Predicted vs Actual with Confidence Intervals")
plt.show()

# T-tests between models
print("T-test LSTM vs GRU:", ttest_rel(pred_lstm_actual, pred_gru_actual).pvalue)
print("T-test LSTM vs CNN:", ttest_rel(pred_lstm_actual, pred_cnn_actual).pvalue)
print("T-test GRU vs CNN:", ttest_rel(pred_gru_actual, pred_cnn_actual).pvalue)

# 1. Select a representative sample from training data
background = X_train[np.random.choice(X_train.shape[0], 100, replace=False)]

# 2. Create explainer - Use KernelExplainer as fallback
def model_predict(X):
    """Reshape data for model prediction"""
    if len(X.shape) == 2:
        X = X.reshape(-1, X_train.shape[1], X_train.shape[2])
    return best_lstm.predict(X, verbose=0)

explainer = shap.KernelExplainer(model_predict, background.mean(axis=0).reshape(1, -1))

# 3. Calculate SHAP values for test samples
X_shap = X_test[:50].reshape(50, -1)  # Flatten time steps and features
shap_values = explainer.shap_values(X_shap)

# 4. Reshape and plot
feature_names = ['close','MA_7','MA_30','Volatility','RSI']
time_step_names = [f't-{i}' for i in range(X_train.shape[1]-1, -1, -1)]

# Aggregate absolute SHAP values across time steps
shap_abs = np.abs(shap_values).mean(axis=0)
shap_abs = shap_abs.reshape(X_train.shape[1], len(feature_names))

# Create heatmap of feature importance over time
plt.figure(figsize=(12, 8))
sns.heatmap(shap_abs,
           xticklabels=feature_names,
           yticklabels=time_step_names,
           cmap='viridis')
plt.title("SHAP Value Importance Across Time Steps")
plt.xlabel("Features")
plt.ylabel("Time Steps")
plt.show()

# Alternative: Bar plot of overall feature importance
plt.figure(figsize=(10, 5))
shap.summary_plot(shap_values, X_shap,
                 feature_names=[f"{t}_{f}" for t in time_step_names for f in feature_names],
                 plot_type='bar',
                 show=False)
plt.title("Overall Feature Importance")
plt.tight_layout()
plt.show()
