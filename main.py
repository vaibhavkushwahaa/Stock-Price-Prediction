from flask import Flask, render_template , request
from prophet_with_flask import plot_price, plot_candlestick, prediction_model,future_prediction, plot_moving_average, yahoo_stocks, get_stock_info, get_stock_news
import os
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/news/india')
def news_india():
    # Initialize the NewsAPI client
    newsapi = NewsApiClient(api_key='476a461dcd964f0b8d1da096ebbebd7e')

    # Fetch the top headlines for India
    top_headlines = newsapi.get_top_headlines(country="in")

    # Extract the relevant data from the API response
    articles = top_headlines['articles']
   

    return render_template('news_india.html', news_items=articles)

@app.route('/news/world')
def news_world():
    # Initialize the NewsAPI client
    newsapi = NewsApiClient(api_key='476a461dcd964f0b8d1da096ebbebd7e')

    # Fetch the top headlines for the world
    top_headlines = newsapi.get_top_headlines(q="world")

    # Extract the relevant data from the API response
    articles = top_headlines['articles']
   

    return render_template('news_world.html', news_items=articles)

@app.route('/news/business')
def news_buisness():
    # Initialize the NewsAPI client
    newsapi = NewsApiClient(api_key='476a461dcd964f0b8d1da096ebbebd7e')

    # Fetch the top headlines for the world
    top_headlines = newsapi.get_top_headlines(category="business")

    # Extract the relevant data from the API response
    articles = top_headlines['articles']
    return render_template('news_buisness.html', news_items=articles)

@app.route('/news/economy')
def news_economy():
    # Initialize the NewsAPI client
    newsapi = NewsApiClient(api_key='476a461dcd964f0b8d1da096ebbebd7e')

    # Fetch the top headlines for the world
    top_headlines = newsapi.get_top_headlines(category="general")

    # Extract the relevant data from the API response
    articles = top_headlines['articles']


    return render_template('news_economy.html', news_items=articles)

@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        df_whole = yahoo_stocks(stock_symbol)
        stock_info = get_stock_info(stock_symbol)
        price_plot = plot_price(df_whole)
        candlestick_plot = plot_candlestick(df_whole)
        news_items = get_stock_news(stock_symbol)
        ohlc_data = df_whole[['Date', 'Open', 'High', 'Low', 'Close']][-5: ]

        return render_template('stocks.html', 
                               stock_symbols=STOCK_SYMBOLS, 
                               stock=STOCK_SYMBOLS[stock_symbol], 
                               stock_info=stock_info, 
                               price_plot=price_plot, 
                               candlestick_plot=candlestick_plot, 
                               news_items=news_items,
                               ohlc_data=ohlc_data)
    return render_template('stocks.html', stock_symbols=STOCK_SYMBOLS)

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        df_whole = yahoo_stocks(stock_symbol)
        prediction_plot = prediction_model(df_whole)
        future_plot, future_table = future_prediction(df_whole)
        moving_average_plot = plot_moving_average(df_whole)
        return render_template('prediction.html', stock_symbols=STOCK_SYMBOLS, stock=STOCK_SYMBOLS[stock_symbol], prediction_plot=prediction_plot, future_plot=future_plot, future_table=future_table, moving_average_plot=moving_average_plot)
    return render_template('prediction.html', stock_symbols=STOCK_SYMBOLS)



@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run( debug=True)
