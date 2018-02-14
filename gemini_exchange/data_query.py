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