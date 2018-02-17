from common_data_query import CommonCoinData

REQUEST_DURATION = 4

class GeminiCoinData(CommonCoinData):
    def __init__(self, exchange_api, ask=None, bid=None, last=None, bitcoin=None, ether=None):
        self.ether_USD_bid = 0
        self.ether_USD_ask = 0
        self.ether_USD_lasttrade = 0
        self.bitcoin_USD_bid = 0
        self.bitcoin_USD_ask = 0
        self.bitcoin_USD_lasttrade = 0
        self.ask_key = ask
        self.bid_key = bid
        self.last_key = last
        self.bitcoin_key = bitcoin
        self.ether_key = ether
        self.query_thread = None
        self.gemini = exchange_api
        self.name = 'gemini'
        self.trailing_array = []
        self.spread = 0
        self.growth_rate = 0
        super(GeminiCoinData, self).__init__(exchange=self, request_duration=REQUEST_DURATION)

    def get_limit_price(self, type, order_volume, coin):
        """
        Gets the limit price of an order by adding up each order until it reaches total volume
        once it reaches total volume exit and return the price of that order
        :return:
        """

        order_book = self.gemini.get_order_book(coin)

        total_volume = 0.0
        current_price = 0.0
        entries = order_book[type]
        first_entry = entries[0]
        current_price = first_entry['price']

        for entry in order_book[type]:
            volume = entry['amount']
            total_volume += float(volume)
            if total_volume >= float(order_volume):
                print current_price
                return float(current_price)

        return 0

    def update_bitcoins(self):
        bitcoin = self.gemini.get_ticker(self.bitcoin_key)
        self.bitcoin_USD_ask= bitcoin[self.ask_key]
        self.bitcoin_USD_bid = bitcoin[self.bid_key]
        self.bitcoin_USD_lasttrade = bitcoin[self.last_key]

    def update_ether(self):
        ether = self.gemini.get_ticker(self.ether_key)
        self.ether_USD_ask = ether[self.ask_key]
        self.ether_USD_bid = ether[self.bid_key]
        self.ether_USD_lasttrade = ether[self.last_key]

    def update_litecoins(self):
        return


    def update_coins(self, coins):
        if 'bitcoin' in coins:
            bitcoin = self.gemini.get_ticker(self.bitcoin_key)
            self.bitcoin_USD_ask = bitcoin[self.ask_key]
            self.bitcoin_USD_bid = bitcoin[self.bid_key]
            self.bitcoin_USD_lasttrade = bitcoin[self.last_key]
        if 'ether' in coins:
            ether = self.gemini.get_ticker(self.ether_key)
            self.ether_USD_ask = ether[self.ask_key]
            self.ether_USD_bid = ether[self.bid_key]
            self.ether_USD_lasttrade = ether[self.last_key]