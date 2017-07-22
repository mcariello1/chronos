
from common_data_query import CommonCoinData

REQUEST_DURATION = 3

class PoloniexCoinData(CommonCoinData):
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
        self.poloniex = exchange_api
        self.name = 'poloniex_exchange'

        super(PoloniexCoinData, self).__init__(exchange=self, request_duration=REQUEST_DURATION)



    def update_litecoins(self):
        """
        Queries and updates all lite coin information for this exchange
        :return:
        """
        litecoin = self.poloniex.returnTicker()[self.litecoin_key]
        self.litecoin_USD_ask = litecoin[self.ask_key]
        self.litecoin_USD_bid = litecoin[self.bid_key]
        self.litecoin_USD_lasttrade = litecoin[self.last_key]

    def update_bitcoins(self):
        """
        Queries and updates all bitcoin information for this exchange
        :return:
        """
        bitcoin = self.poloniex.returnTicker()[self.bitcoin_key]
        self.bitcoin_USD_ask = bitcoin[self.ask_key]
        self.bitcoin_USD_bid = bitcoin[self.bid_key]
        self.bitcoin_USD_lasttrade = bitcoin[self.last_key]

    def update_ether(self):
        """
        Queries and updates all ether information for this exchange
        :return:
        """
        ether = self.poloniex.returnTicker()[self.ether_key]
        self.ether_USD_ask = ether[self.ask_key]
        self.ether_USD_bid = ether[self.bid_key]
        self.ether_USD_lasttrade = ether[self.last_key]
