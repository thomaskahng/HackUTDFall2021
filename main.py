import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import finnhub
import plotly.graph_objects as go
import plotly.io as pio

from datetime import datetime
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
today = datetime.now().strftime("%Y-%m-%d")
last_year = datetime.strftime(datetime.now() - timedelta(365), '%Y-%m-%d')

# Enter your API key here
key = "sandbox_c683gniad3iagio36rkg"
finn_client = finnhub.Client(api_key=key)

# app = Flask(__name__)

def restructure(arrays_none, arrays_last12):
    # Reformat lists
    for elem in arrays_last12:
        arrays_last12[elem].reverse()

    for elem in arrays_none:
        arrays_none[elem].reverse()


def get_data(data, arrays_none, arrays_last12):
    temp = 0

    # Stock information
    for data_elem in data:
        for key, value in data_elem.items():
            # Put into dictionary by count of value (split by year)
            if 0 <= temp <= 11:
                arrays_last12[key].append(value)
            else:
                arrays_none[key].append(value)
        temp += 1

def show_stock_recommendations(stock, arrays_last12):
    # Plot recommendations
    plt.plot(arrays_last12['period'], arrays_last12['buy'],
             color='r', marker='o')
    plt.plot(arrays_last12['period'], arrays_last12['strongBuy'],
             color='m', marker='o')
    plt.plot(arrays_last12['period'], arrays_last12['sell'],
             color='g', marker='o')
    plt.plot(arrays_last12['period'], arrays_last12['strongSell'],
             color='c', marker='o')
    plt.plot(arrays_last12['period'], arrays_last12['hold'],
             color='b', marker='o')

    # Modify plot
    plt.xticks(rotation=90)
    plt.xlabel('Month')
    plt.ylabel('Number of Recommendations')
    plt.title(f"{stock} Analyst Recommendations Past 12 Months")

    # SHow legend and plot
    plt.legend(['buy', 'strongBuy', 'sell', 'strongSell', 'hold'], loc='center left',
               bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.grid()
    plt.savefig('static/recommendations.png')

def show_stock_candles(stock, candle_data):
    # Plot stock candle data
    figure = go.Figure(
        data=[
            go.Candlestick(
                x=candle_data['t'],
                low=candle_data['l'],
                high=candle_data['h'],
                close=candle_data['c'],
                open=candle_data['o'],
                increasing_line_color='green',
                decreasing_line_color='red'
            )
        ]
    )
    figure.update_layout(
        title=f"{stock} Price",
        yaxis_title=f"{stock} Price USD ($)",
        xaxis_title='Date (Month)',
    )
    pio.write_image(figure, 'static/stock.png')

@app.route("/", methods=['GET', 'POST'])
def logic():
    stock = ""
    if request.method == "POST":
        # Ask user for stock and get info
        stock = str(request.form.get("stock")).upper()
        data = finn_client.recommendation_trends(stock)

        # See if stock exists
        exists = False
        if len(data) > 0:
            exists = True

        # Convert to unix time to find candles
        unix_today = int(datetime.strptime(today, "%Y-%m-%d").timestamp())
        unix_last_year = int(datetime.strptime(last_year, "%Y-%m-%d").timestamp())

        # Find candle data for stocks
        candle_data = finn_client.stock_candles(stock, 'W', unix_last_year, unix_today)
        for i in range (0, len(candle_data['t'])):
            candle_data['t'][i] = datetime.utcfromtimestamp(candle_data['t'][i]).strftime('%Y-%m-%d')

        # Store data by year
        arrays_none = {'buy': [], 'hold': [], 'period': [], 'sell': [],
                       'strongBuy': [], 'strongSell': [], 'symbol': []}
        arrays_last12 = {'buy': [], 'hold': [], 'period': [], 'sell': [],
                         'strongBuy': [], 'strongSell': [], 'symbol': []}

        # See if stock exists
        if exists is True:
            get_data(data, arrays_none, arrays_last12)
            restructure(arrays_none, arrays_last12)

            show_stock_recommendations(stock, arrays_last12)
            show_stock_candles(stock, candle_data)
            return render_template("charts.html", stock=stock)
        else:
            return render_template("home.html", no_stock=True)
    return render_template("home.html", stock=stock, no_stock=False)

@app.route("/charts", methods=['GET', 'POST'])
def data():
    # Return result in charts if possible
    if request.method == 'POST':
        return redirect(url_for('logic'))
    else:
        return render_template("charts.html")

if __name__ == "__main__":
    app.run(debug=True)