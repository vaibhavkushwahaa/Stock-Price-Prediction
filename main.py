from flask import Flask, render_template , request, redirect, flash, session
from prophet_with_flask import plot_technical_indicators,plot_components,get_metadata,plot_price, plot_candlestick, prediction_model,future_prediction, plot_moving_average, yahoo_stocks, get_stock_info, get_stock_news
import os
from newsapi import NewsApiClient
from database import User, Contact, open_db, get_all, save, StarredStock, Report


app = Flask(__name__)
app.secret_key  = 'super secret key'

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
    "JPM": "JPMorgan Chase & Co.",
    "NFLX": "Netflix, Inc."
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(username) == 0 or len(password) == 0:
            flash('Please fill in all the fields', 'danger')
            return redirect('/login')
        db = open_db()
        if db.query(User).filter(User.username == username, User.password == password).count() == 1:
            user = db.query(User).filter(User.username == username, User.password == password).first()
            session['username'] = user.username
            session['id'] = user.id
            session['email'] = user.email
            session['isauth'] = True
            flash('Login successful', 'success')
            return redirect('/')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if len(username) == 0 or len(email) == 0 or len(password) == 0:
            flash('Please fill in all the fields', 'danger')
            return redirect('/register')
        db = open_db()
        # check if email already exists
        if db.query(User).filter(User.email == email).count()>0:
            flash('Email already exists', 'danger')
            return redirect('/register')
        # check if username already exists
        if db.query(User).filter(User.username == username).count()>0:
            flash('Username already exists', 'danger')
            return redirect('/register')
        try:
            user = User(username=username, email=email, password=password)
            save( user)
            flash('User registered successfully', 'success')
            return redirect('/login')
        except Exception as e:
            flash(f'An error occurred {e}')
            return redirect('/register')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/news/india')
def news_india():
    if not session.get('isauth'):
        flash('Please login to view this page', 'danger')
        return redirect('/login')
    # Initialize the NewsAPI client
    newsapi = NewsApiClient(api_key='476a461dcd964f0b8d1da096ebbebd7e')

    # Fetch the top headlines for India
    top_headlines = newsapi.get_top_headlines(country="in")

    # Extract the relevant data from the API response
    articles = top_headlines['articles']
   

    return render_template('news_india.html', news_items=articles)

@app.route('/news/world')
def news_world():
    if not session.get('isauth'):
        flash('Please login to view this page', 'danger')
        return redirect('/login')
    # Initialize the NewsAPI client
    newsapi = NewsApiClient(api_key='476a461dcd964f0b8d1da096ebbebd7e')

    # Fetch the top headlines for the world
    top_headlines = newsapi.get_top_headlines(q="world")

    # Extract the relevant data from the API response
    articles = top_headlines['articles']
   

    return render_template('news_world.html', news_items=articles)

@app.route('/news/business')
def news_buisness():
    if not session.get('isauth'):
        flash('Please login to view this page', 'danger')
        return redirect('/login')
    # Initialize the NewsAPI client
    newsapi = NewsApiClient(api_key='476a461dcd964f0b8d1da096ebbebd7e')

    # Fetch the top headlines for the world
    top_headlines = newsapi.get_top_headlines(category="business")

    # Extract the relevant data from the API response
    articles = top_headlines['articles']
    return render_template('news_buisness.html', news_items=articles)

@app.route('/news/economy')
def news_economy():
    if not session.get('isauth'):
        flash('Please login to view this page', 'danger')
        return redirect('/login')
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
        stock_metadata = get_metadata(stock_symbol)

        return render_template('stocks.html', 
                               stock_symbols=STOCK_SYMBOLS, 
                               stock=STOCK_SYMBOLS[stock_symbol], 
                               stock_info=stock_info, 
                               price_plot=price_plot, 
                               candlestick_plot=candlestick_plot, 
                               news_items=news_items,
                               ohlc_data=ohlc_data,
                               stock_metadata=stock_metadata)
    return render_template('stocks.html', stock_symbols=STOCK_SYMBOLS)

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        df_whole = yahoo_stocks(stock_symbol)
        prediction_plot = prediction_model(df_whole)
        future_plot, future_table = future_prediction(df_whole)
        moving_average_plot = plot_moving_average(df_whole)
        components_plot = plot_components(df_whole)
        technical_indicators_plot = plot_technical_indicators(df_whole)
        
        return render_template('prediction.html',
                                stock_symbols=STOCK_SYMBOLS,
                                stock=STOCK_SYMBOLS[stock_symbol],
                                prediction_plot=prediction_plot,
                                future_plot=future_plot, future_table=future_table, 
                                moving_average_plot=moving_average_plot, 
                                components_plot=components_plot,
                                technical_indicators_plot=technical_indicators_plot)
    return render_template('prediction.html', stock_symbols=STOCK_SYMBOLS)



@app.route('/contact')
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        subject = request.form['subject']
        try:
            contact = Contact(name=name, email=email, message=message, subject=subject)
            save(contact)
            flash('Message sent successfully', 'success')
            return redirect('/contact')
        except Exception as e:
            flash(f'An error occurred {e}')
            return redirect('/contact')
    return render_template('contact.html')


# mark as fav
@app.route('/markfav', methods=['GET', 'POST'])
def mark_as_fav():
    if not session.get('isauth'):
        flash('Please login to view this page', 'danger')
        return redirect('/login')
    # get the stock symbol from s and name from n
    stock_symbol = request.args.get('s')
    stock_name = request.args.get('n')
    if not stock_symbol:
        flash('Invalid request', 'danger')
        return redirect('/stocks')
    if not stock_name:
        flash('Invalid request, no stock name found', 'danger')
        return redirect('/stocks')
    db = open_db()
    user_id = session.get('id')
    stock = db.query(StarredStock).filter(StarredStock.stock_symbol == stock_symbol, StarredStock.user_id == user_id).first()
    if stock:
        flash('Stock already marked as favourite', 'warning')
        return redirect('/stocks')
    try:
        stock = StarredStock(stock_symbol=stock_symbol, user_id=user_id)
        save(stock)
        flash(f'{stock_name} marked as favourite', 'success')
        return redirect('/stocks')
    except Exception as e:
        flash(f'An error occurred {e}')
        return redirect('/stocks')
    
@app.route('/favs')
def fav_stocks():
    if not session.get('isauth'):
        flash('Please login to view this page', 'danger')
        return redirect('/login')
    db = open_db()
    user_id = session.get('id')
    stocks = db.query(StarredStock).filter(StarredStock.user_id == user_id).all()
    return render_template('favs.html', stocks=stocks)

@app.route('/removefav/<int:id>')
def remove_fav(id):
    if not session.get('isauth'):
        flash('Please login to view this page', 'danger')
        return redirect('/login')
    db = open_db()
    stock = db.query(StarredStock).filter(StarredStock.id == id).first()
    if not stock:
        flash('Stock not found', 'danger')
        return redirect('/favs')
    try:
        db.delete(stock)
        db.commit()
        flash('Stock removed from favourites', 'success')
        return redirect('/favs')
    except Exception as e:
        flash(f'An error occurred {e}')
        return redirect('/favs')

if __name__ == '__main__':
    app.run( debug=True)
