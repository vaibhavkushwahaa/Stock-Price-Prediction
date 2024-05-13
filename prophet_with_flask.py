from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import numpy as np
from prophet import Prophet
import yfinance as yf
import matplotlib.pyplot as plt
from prophet.plot import plot_plotly
from sklearn.metrics import mean_absolute_error
import plotly.graph_objects as go
from newsapi import NewsApiClient

app = Flask(__name__)
STOCK_SYMBOLS = {
    "RELIANCE.NS": "Reliance Industries Limited",
    "TCS.NS": "Tata Consultancy Services Limited",
    "INFY.NS": "Infosys Limited",
    "HDFCBANK.NS": "HDFC Bank Limited",
    "SBI.NS": "State Bank of India",
    "ICICIBANK.NS": "ICICI Bank Limited",
    "HINDUNILVR.NS": "Hindustan Unilever Limited",
    "AXISBANK.NS": "Axis Bank Limited",
    "WIPRO.NS": "Wipro Limited",
    "BHARTIARTL.NS": "Bharti Airtel Limited",
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com Inc.",
    "GOOGL": "Google Inc.",
    "TSLA": "Tesla, Inc.",
    "FB": "Meta Platforms, Inc.",
    "JPM": "JPMorgan Chase & Co."
}
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        df_whole = yahoo_stocks(stock_symbol)
        price_plot = plot_price(df_whole)
        candlestick_plot = plot_candlestick(df_whole)
        prediction_plot = prediction_model(df_whole)
        future_plot, future_table = future_prediction(df_whole)
        moving_average_plot = plot_moving_average(df_whole)
        return render_template('index.html', stock_symbols=STOCK_SYMBOLS, stock=STOCK_SYMBOLS[stock_symbol], price_plot=price_plot, candlestick_plot=candlestick_plot, prediction_plot=prediction_plot, future_plot=future_plot, future_table=future_table, moving_average_plot=moving_average_plot)
    return render_template('index.html', stock_symbols=STOCK_SYMBOLS)

def yahoo_stocks(stock_symbol):
    stock_data = yf.download(stock_symbol, period='1y', interval='1d')
    stock_data = stock_data.reset_index()
    
    if 'Date' in stock_data.columns and 'Adj Close' in stock_data.columns:
        stock_data['ds'] = stock_data['Date']
        stock_data['y'] = stock_data['Adj Close']
        
        return stock_data
    
    else:
        print(f"Error: The stock_data DataFrame does not have the expected 'Date' and 'Adj Close' columns for stock symbol: {stock_symbol}")
        return None

def plot_price(df_whole):
    fig = px.line(df_whole, x='Date', y='Close')
    fig.update_xaxes(rangeslider_visible=False)
    return fig.to_html(full_html=False)

def get_stock_info(stock_symbol):
    stock_data = yf.Ticker(stock_symbol)
    stock_info = stock_data.info
    return stock_info

def get_stock_news(stock_symbol):
    newsapi = NewsApiClient(api_key='476a461dcd964f0b8d1da096ebbebd7e')
    news_articles = newsapi.get_everything(q=stock_symbol, language='en', sort_by='relevancy')['articles']
    news_items = []
    for article in news_articles:
        news_item = {
            'title': article['title'],
            'description': article['description'],
            'url': article['url'],
            'image': article['urlToImage']
        }
        news_items.append(news_item)
    return news_items

def plot_candlestick(df_whole):
    fig = go.Figure(data=[go.Candlestick(
        x=df_whole['Date'],
        open=df_whole['Open'],
        high=df_whole['High'],
        low=df_whole['Low'],
        close=df_whole['Close']
    )])

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False
    )
    return fig.to_html(full_html=False)

def prediction_model(df_whole):
    train_data = df_whole.sample(frac=0.8, random_state=0)
    test_data = df_whole.drop(train_data.index)

    model_1 = Prophet(daily_seasonality=True)
    model_1.fit(train_data)

    y_actual = test_data['y']
    prediction = model_1.predict(pd.DataFrame({'ds': test_data['ds']}))
    y_predicted = prediction['yhat'].astype(int)
    mean_absolute_error(y_actual, y_predicted)
    prediction = model_1.predict(pd.DataFrame({'ds':test_data['ds']}))

    trace_predicted = go.Scatter(x=test_data['ds'], y=y_predicted, mode='lines', name='Predicted', line=dict(color='black'))
    trace_actual = go.Scatter(x=test_data['ds'], y=y_actual, mode='lines', name='Actual', line=dict(color='yellow'))
    layout = go.Layout(
        title="Price Action: Predicted vs Actual",
        xaxis=dict(title="Year"),
        yaxis=dict(title="Price Action"),
        showlegend=True)
    fig = go.Figure(data=[trace_predicted, trace_actual], layout=layout)
    return fig.to_html(full_html=False)

def future_prediction(df_whole):
    model_2 = Prophet()
    model_2.fit(df_whole)
    future = model_2.make_future_dataframe(365)
    forecast = model_2.predict(future)
    fig = plot_plotly(model_2, forecast)
    fig.update_xaxes(rangeslider_visible=False)
    forecast_table = forecast[['ds','yhat','yhat_lower','yhat_upper']].tail().to_html()
    return fig.to_html(full_html=False), forecast_table

def plot_moving_average(df_whole, window_size=20):
    df_whole['MA'] = df_whole['Close'].rolling(window=window_size).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_whole['Date'], y=df_whole['Close'], mode='lines', name='Actual Price'))
    fig.add_trace(go.Scatter(x=df_whole['Date'], y=df_whole['MA'], mode='lines', name='Moving Average'))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False
    )
    return fig.to_html(full_html=False)

if __name__ == '__main__':
    app.run(debug=True)