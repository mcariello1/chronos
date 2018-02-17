
from common_data_query import CommonCoinData
import gdax
import time
REQUEST_DURATION = 3

class GdaxCoinData(CommonCoinData):
    def __init__(self, ask=None, bid=None, last=None, bitcoin=None, litecoin=None, ether=None):
        self.litecoin_USD_bid = 0.0
        self.litecoin_USD_ask = 0.0
        self.litecoin_USD_lasttrade = 0.0
        self.ether_USD_bid = 0.0
        self.ether_USD_ask = 0.0
        self.ether_USD_lasttrade = 0.0
        self.bitcoin_USD_bid = 0.0
        self.bitcoin_USD_ask = 0.0
        self.bitcoin_USD_lasttrade = 0.0
        self.ask_key = ask
        self.bid_key = bid
        self.last_key = last
        self.coinbase = gdax.PublicClient()
        self.litecoin_key = litecoin
        self.bitcoin_key = bitcoin
        self.ether_key = ether
        self.order_volume = None
        self.name = 'gdax'
        super(GdaxCoinData, self).__init__(exchange=self, request_duration=REQUEST_DURATION)

    def get_limit_price(self, type, order_volume, coin_id):
        """
        Gets the limit price of an order by adding up each order until it reaches total volume
        once it reaches total volume exit and return the price of that order
        :type: asks or bids
        :return:
        """


        time.sleep(2)
        book = self.coinbase.get_product_order_book(coin_id, level=2)
        entries = book[type]
        while len(entries) < 1:
            time.sleep(3)
            book = self.coinbase.get_product_order_book(coin_id, level=2)
            entries = book[type]
        total_volume = 0.0
        current_price = 0.0
        current_price, volume, order_id = entries[0]
        for price, volume, order_id in entries:
            print price
            print volume
            print order_id
            total_volume += float(volume)
            print 'total' + str(total_volume)
            print 'order' + str(order_volume)
            print 'price' + str(price)
            if total_volume >= float(order_volume):
                print current_price
                return float(current_price)

        return 0

    def update_litecoins(self):
        """
        Queries and updates litecoin information from gdax /coinbase
        :return:
        """

        litecoin = self.coinbase.get_product_ticker(self.litecoin_key)
        self.litecoin_USD_ask = litecoin[self.ask_key]
        self.litecoin_USD_bid = litecoin[self.bid_key]

    def update_bitcoins(self):
        """
        Queries and updates bitcoin information from gdax/coinbase
        :return:
        """
        bitcoin = self.coinbase.get_product_ticker(self.bitcoin_key)
        self.bitcoin_USD_ask = float(bitcoin[self.ask_key])
        self.bitcoin_USD_bid = float(bitcoin[self.bid_key])

    def update_ether(self):
        """
        Queries and updates ether information from gdax/coinbase
        :return:
        """
        ether = self.coinbase.get_product_ticker(self.ether_key)
        self.ether_USD_ask = float(ether[self.ask_key])
        self.ether_USD_bid = float(ether[self.bid_key])


    def update_coins(self, coins):
        if 'ether' in coins:
            ether = self.coinbase.get_product_ticker(self.ether_key)
            self.ether_USD_ask = float(ether[self.ask_key])
            self.ether_USD_bid = float(ether[self.bid_key])
        if 'bitcoin' in coins:
            bitcoin = self.coinbase.get_product_ticker(self.bitcoin_key)
            self.bitcoin_USD_ask = float(bitcoin[self.ask_key])
            self.bitcoin_USD_bid = float(bitcoin[self.bid_key])
        if 'litecoin' in coins:
            litecoin = self.coinbase.get_product_ticker(self.litecoin_key)
            self.litecoin_USD_ask = litecoin[self.ask_key]
            self.litecoin_USD_bid = litecoin[self.bid_key]