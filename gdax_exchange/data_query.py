
from common_data_query import CommonCoinData
import gdax

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

    def get_limit_price(self, type):
        """
        Gets the limit price of an order by adding up each order until it reaches total volume
        once it reaches total volume exit and return the price of that order
        :return:
        """

        order_book = gdax.OrderBook(product_id='ETH-USD')
        order_book.start()

        book = order_book.get_current_book()
        entries = book[type]

        total_volume = 0.0
        current_price = 0.0

        for price, volume, order_id in entries:
            current_price = price
            total_volume += volume
            if total_volume >= float(self.order_volume):
                break

        order_book.close()

        return float(current_price)

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
