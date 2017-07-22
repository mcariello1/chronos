from common_data_query import CommonCoinData


#time.sleep(10)

class BitfinexCoinData(CommonCoinData):
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
        #self.litecoin_ticker = 'ltcusd'
        #self.bitcoin_ticker = 'btcusd'
        #self.ether_ticker = 'ethusd'
        #self.ask_key = 'ask'
        #self.bid_key = 'bid'
        #self.last_key = 'last_price'
        self.ask_key = ask
        self.bid_key = bid
        self.last_key = last
        self.litecoin_key = litecoin
        self.bitcoin_key = bitcoin
        self.ether_key = ether
        self.bitfx = exchange_api
        #self.bitfx = bitfinex.Client()
        self.name = 'bitfinex_exchange'
        super(BitfinexCoinData, self).__init__(exchange=self, request_duration=10)



    def update_litecoins(self):
        self.litecoin_USD_ask = self.bitfx.ticker(self.litecoin_key)[self.ask_key]
        self.litecoin_USD_bid = self.bitfx.ticker(self.litecoin_key)[self.bid_key]
        self.litecoin_USD_lasttrade = self.bitfx.ticker(self.litecoin_key)[self.last_key]

    def update_bitcoins(self):
        self.bitcoin_USD_ask = self.bitfx.ticker(self.bitcoin_key)[self.ask_key]
        self.bitcoin_USD_bid = self.bitfx.ticker(self.bitcoin_key)[self.bid_key]
        self.bitcoin_USD_lasttrade = self.bitfx.ticker(self.bitcoin_key)[self.last_key]

    def update_ether(self):
        self.ether_USD_ask = self.bitfx.ticker(self.ether_key)[self.ask_key]
        self.ether_USD_bid = self.bitfx.ticker(self.ether_key)[self.bid_key]
        self.ether_USD_lasttrade = self.bitfx.ticker(self.ether_key)[self.last_key]

