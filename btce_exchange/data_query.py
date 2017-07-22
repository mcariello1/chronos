
import btceapi

from common_data_query import CommonCoinData

REQUEST_DURATION = 3

class BtceCoinData(CommonCoinData):
    def __init__(self, exchange_api, exchange_info, bitcoin=None, litecoin=None, ether=None):
        self.litecoin_USD_bid = 0
        self.litecoin_USD_ask = 0
        self.litecoin_USD_lasttrade = 0
        self.ether_USD_bid = 0
        self.ether_USD_ask = 0
        self.ether_USD_lasttrade = 0
        self.bitcoin_USD_bid = 0
        self.bitcoin_USD_ask = 0
        self.bitcoin_USD_lasttrade = 0
        self.bitcoin_key = bitcoin
        self.litecoin_key = litecoin
        self.ether_key = ether
        self.btce = exchange_api
        self.info = exchange_info
        self.name = 'btce_exchange'
        self.trailing_array = []
        self.spread = 0
        self.growth_rate = 0
        super(BtceCoinData, self).__init__(exchange=self, request_duration=REQUEST_DURATION)



    def update_bitcoins(self):
        bitcoin = btceapi.getTicker(self.bitcoin_key, self.btce, self.info)
        self.bitcoin_USD_ask= bitcoin.buy
        self.bitcoin_USD_bid = bitcoin.sell
        self.bitcoin_USD_lasttrade = bitcoin.last

    def update_ether(self):
        ether = btceapi.getTicker(self.ether_key, self.btce, self.info)
        self.ether_USD_ask = ether.buy
        self.ether_USD_bid = ether.sell
        self.ether_USD_lasttrade = ether.last

    def update_litecoins(self):
        litecoin = btceapi.getTicker(self.litecoin_key, self.btce, self.info)
        self.litecoin_USD_ask = litecoin.buy
        self.litecoin_USD_bid = litecoin.sell
        self.litecoin_USD_lasttrade = litecoin.last
