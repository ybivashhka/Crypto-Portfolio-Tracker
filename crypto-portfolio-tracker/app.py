# Crypto Portfolio Tracker with Stylish Web Interface, Interactive Coin Search, and TradingView Chart
# Fixed chart symbol: fetch ticker symbol (e.g., 'ETH' for 'ethereum') from CoinGecko for correct TradingView symbol (BINANCE:ETHUSDT).
# Made chart resizable (vertical) and draggable (like a window) with JS.
# Improved readability: increased default height, ensured dark theme consistency.
# Libraries: flask, requests, pandas.

from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd

app = Flask(__name__)

# Function to get current price
def get_crypto_price(crypto_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get(crypto_id, {}).get('usd')
    return None

# Function to get crypto symbol (ticker like 'eth')
def get_crypto_symbol(crypto_id):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('symbol', crypto_id[:3]).upper()  # Fallback to first 3 letters if no symbol
    return crypto_id[:3].upper()

# Function to calculate portfolio value
def calculate_portfolio_value(portfolio):
    total_value = 0
    details = []
    for crypto_id, amount in portfolio.items():
        price = get_crypto_price(crypto_id)
        symbol = get_crypto_symbol(crypto_id)
        if price:
            value = amount * price
            total_value += value
            details.append({'Symbol': symbol, 'Amount': amount, 'Price (USD)': price, 'Value (USD)': value})
        else:
            details.append({'Symbol': symbol, 'Amount': amount, 'Price (USD)': 'N/A', 'Value (USD)': 'N/A'})
    return total_value, details

# Endpoint for coin search suggestions
@app.route('/search_coins', methods=['GET'])
def search_coins():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])
    url = f"https://api.coingecko.com/api/v3/search?query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        coins = data.get('coins', [])[:10]
        suggestions = [{'id': coin['id'], 'name': coin['name'], 'symbol': coin['symbol'], 'thumb': coin['thumb']} for coin in coins]
        return jsonify(suggestions)
    return jsonify([])

# Default portfolio
default_portfolio = {
    'bitcoin': 0.5,
    'ethereum': 2.0,
    'solana': 100.0
}

@app.route('/', methods=['GET', 'POST'])
def index():
    portfolio = default_portfolio.copy()
    portfolio_list = []
    if request.method == 'POST':
        input_str = request.form.get('portfolio_input')
        if input_str:
            try:
                items = input_str.split(',')
                portfolio = {item.split(':')[0].strip().lower(): float(item.split(':')[1].strip()) for item in items}
            except:
                pass
    portfolio_list = [{'crypto': crypto, 'amount': amount} for crypto, amount in portfolio.items()]

    total_value, details = calculate_portfolio_value(portfolio)
    df_html = pd.DataFrame(details).to_html(index=False, classes='table table-dark table-hover') if details else ""

    crypto_to_plot = request.form.get('crypto_to_plot', 'bitcoin').lower()
    crypto_symbol = get_crypto_symbol(crypto_to_plot) if crypto_to_plot else 'BTC'

    return render_template('index.html', table=df_html, total_value=total_value, current_crypto=crypto_to_plot, portfolio_list=portfolio_list, crypto_symbol=crypto_symbol)

if __name__ == '__main__':
    app.run(debug=True)