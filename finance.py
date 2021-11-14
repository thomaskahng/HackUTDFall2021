import finnhub
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta

today = datetime.now().strftime("%Y-%m-%d")
yesterday = datetime.strftime(datetime.now() - timedelta(365), '%Y-%m-%d')

key = "sandbox_c683gniad3iagio36rkg"
finn_client = finnhub.Client(api_key=key)

class Finance:
        def __init__(self):
            # Ask user for stock and get info
            self.stock = input("Enter stock: ")
            self.data = finn_client.recommendation_trends(self.stock)
            # self.candle_data = finn_client.stock_candles(self.stock, 'D', )

            # See if stock exists
            self.exists = False
            self.stock_exists()

            # Store data by year
            self.arrays_none = {'buy': [], 'hold': [], 'period': [], 'sell': [],
                                'strongBuy': [], 'strongSell': [], 'symbol': []}
            self.arrays_last12 = {'buy': [], 'hold': [], 'period': [], 'sell': [],
                                'strongBuy': [], 'strongSell': [], 'symbol': []}

            # Retrieve data and plot
            self.get_data()
            self.restructure()
            self.show_stock_recommendations()
            self.show_stock_candles()

        def stock_exists(self):
            if len(self.data) > 0:
                self.exists = True

        def restructure(self):
            if self.exists:
                for elem in self.arrays_last12:
                    self.arrays_last12[elem].reverse()

                for elem in self.arrays_none:
                    self.arrays_none[elem].reverse()

        def get_data(self):
            if self.exists:
                temp = 0

                # Stock information
                for data in self.data:
                    for key, value in data.items():
                        # Put into dictionary by count of value (split by year)
                        if 0 <= temp <= 11:
                            self.arrays_last12[key].append(value)
                        else:
                            self.arrays_none[key].append(value)
                    temp += 1


        def show_stock_recommendations(self):
            if self.exists:
                plt.plot(self.arrays_last12['period'], self.arrays_last12['buy'],
                         color='r', marker='o')
                plt.plot(self.arrays_last12['period'], self.arrays_last12['strongBuy'],
                         color='m', marker='o')
                plt.plot(self.arrays_last12['period'], self.arrays_last12['sell'],
                         color='g', marker='o')
                plt.plot(self.arrays_last12['period'], self.arrays_last12['strongSell'],
                         color='c', marker='o')
                plt.plot(self.arrays_last12['period'], self.arrays_last12['hold'],
                         color='b', marker='o')

                plt.xticks(rotation=90)
                plt.xlabel('Month')
                plt.ylabel('Number of Recommendations')
                plt.title(f"{self.stock} Analyst Recommendations Past 12 Months")

                plt.legend(['buy', 'strongBuy', 'sell', 'strongSell', 'hold'], loc='center left',
                           bbox_to_anchor=(1, 0.5))
                plt.tight_layout()
                plt.grid()
                plt.show()

        def show_stock_candles(self):
            pass