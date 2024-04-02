from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.recycleview import RecycleView
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg as FigureCanvas
from kivy.network.urlrequest import UrlRequest
import yfinance as yf
from fbprophet import Prophet
import matplotlib.pyplot as plt
import pandas as pd

# Dictionary mapping symbols to company names (Indian companies)
companies = {
    'INFY.BO': 'Infosys Limited',
    'TCS.BO': 'Tata Consultancy Services Limited',
    'RELIANCE.BO': 'Reliance Industries Limited',
    # Add more symbols and company names as needed
}

class StockApp(App):

    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Create and place the search label and entry
        self.search_label = Label(text="Enter company name:")
        self.layout.add_widget(self.search_label)
        self.search_entry = TextInput()
        self.layout.add_widget(self.search_entry)

        # Create and place the search button
        self.search_button = Button(text="Search")
        self.search_button.bind(on_press=self.search_click)
        self.layout.add_widget(self.search_button)

        # Create and place the recycleview for search results
        self.search_results = RecycleView()
        self.layout.add_widget(self.search_results)

        # Create and place the date range selection
        self.date_label = Label(text="Select date range:")
        self.layout.add_widget(self.date_label)
        # Use a custom date picker or another approach for date selection

        # Create and place the load button
        self.load_button = Button(text="Load Historical Data and Forecast")
        self.load_button.bind(on_press=self.load_click)
        self.layout.add_widget(self.load_button)

        return self.layout

    def search_click(self, instance):
        search_term = self.search_entry.text.lower()
        self.search_results.data = [{'text': f"{symbol}: {company}"} for symbol, company in companies.items() if search_term in company.lower()]

    def load_click(self, instance):
        selected_index = self.search_results.selected_nodes
        if selected_index:
            selected_symbol = self.search_results.data[selected_index[0]]['text'].split(':')[0].strip()
            self.fetch_stock_data(selected_symbol)

    def fetch_stock_data(self, symbol):
        def on_success(req, result):
            stock_data = self.process_stock_data(symbol, result)
            self.plot_stock_data(stock_data, symbol)

        url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1=0&period2=9999999999&interval=1d&events=history"
        UrlRequest(url, on_success=on_success)

    def process_stock_data(self, symbol, result):
        lines = result.split('\n')
        data = [line.split(',') for line in lines]
        df = pd.DataFrame(data[1:], columns=data[0])
        df['ds'] = pd.to_datetime(df['Date'])
        df['y'] = df['Close'].astype(float)
        return df

    def plot_stock_data(self, stock_data, symbol):
        # Create and train the model
        model = Prophet()
        model.fit(stock_data)

        # Make future predictions
        future = model.make_future_dataframe(periods=365)
        forecast = model.predict(future)

        # Plot the forecast
        fig, ax = plt.subplots()
        ax.plot(stock_data['ds'], stock_data['y'], label='Actual')
        ax.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='--')
        ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.2)
        ax.legend()
        ax.set_title(f"Stock Price Forecast for {companies[symbol]}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        canvas = FigureCanvas(figure=fig)
        self.layout.add_widget(canvas)

if __name__ == '__main__':
    StockApp().run()
