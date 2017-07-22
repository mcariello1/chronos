
from common_data_query import CommonCoinData


REQUEST_DURATION = 3

class GdaxCoinData(CommonCoinData):
    def __init__(self, exchange_api, ask=None, bid=None, last=None, bitcoin=None, litecoin=None, ether=None):
        self.litecoin_USD_bid = 0
        self.litecoin_USD_ask = 0
        self.litecoin_USD_lasttrade = 0
        self.ether_USD_bid = 0
        self.ether_USD_ask = 0
        self.ether_USD_lasttrade = 0
        self.bitcoin_USD_bid = 0
        self.bitcoin_USD_ask = 0
        self.bitcoin_USD_lasttrade = 0
        self.ask_key = ask
        self.bid_key = bid
        self.last_key = last
        self.litecoin_key = litecoin
        self.bitcoin_key = bitcoin
        self.ether_key = ether
        self.coinbase = exchange_api
        self.name = 'gdax_exchange'
        super(GdaxCoinData, self).__init__(exchange=self, request_duration=REQUEST_DURATION)

    def update_litecoins(self):
        """
        Queries and updates litecoin information from gdax /coinbase
        :return:
        """

        litecoin = self.coinbase.get_product_ticker(self.litecoin_key)
        self.litecoin_USD_ask = litecoin[self.ask_key]
        self.litecoin_USD_bid = litecoin[self.bid_key]
        self.litecoin_USD_lasttrade = litecoin[self.last_key]

    def update_bitcoins(self):
        """
        Queries and updates bitcoin information from gdax/coinbase
        :return:
        """
        bitcoin = self.coinbase.get_product_ticker(self.bitcoin_key)
        self.bitcoin_USD_ask = bitcoin[self.ask_key]
        self.bitcoin_USD_bid = bitcoin[self.bid_key]
        self.bitcoin_USD_lasttrade = bitcoin[self.last_key]

    def update_ether(self):
        """
        Queries and updates ether information from gdax/coinbase
        :return:
        """
        ether = self.coinbase.get_product_ticker(self.ether_key)
        self.ether_USD_ask = ether[self.ask_key]
        self.ether_USD_bid = ether[self.bid_key]
        self.ether_USD_lasttrade = ether[self.last_key]
