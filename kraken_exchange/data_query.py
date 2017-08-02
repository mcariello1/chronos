from common_data_query import CommonCoinData

REQUEST_DURATION = 3
LTCUSD = 'XLTCZUSD'
XBTUSD = 'XXBTZUSD'
ETHUSD = 'XETHZUSD'


class KrakenCoinData(CommonCoinData):
    def __init__(self, exchange_api, order_volume, ask=None, bid=None, last=None, bitcoin=None, litecoin=None, ether=None):
        self.kraken = exchange_api
        self.litecoin_USD_bid = 0
        self.litecoin_USD_ask = 0
        self.litecoin_USD_lasttrade = 0
        self.ether_USD_bid = 0
        self.ether_USD_ask = 0
        self.ether_USD_lasttrade = 0
        self.bitcoin_USD_bid = 0
        self.bitcoin_USD_ask = 0
        self.bitcoin_USD_lasttrade = 0
        self.making_transaction = 0
        self.name = 'kraken_exchange'
        self.order_volume = str(order_volume)
        self.keys = {'LTCUSD': LTCUSD, 'XBTUSD': XBTUSD, 'ETHUSD' : ETHUSD}
        super(KrakenCoinData, self).__init__(exchange=self, request_duration=REQUEST_DURATION)



    def get_Depth(self, coin):
        """
        Fetches the order book
        :return:
        """
        json=self.kraken.query_public('Depth', {'pair': coin})

        return json[self.keys[coin]]

    def get_limit_price(self, type, coin):
        """
        Gets the limit price of an order by adding up each order until it reaches total volume
        once it reaches total volume exit and return the price of that order
        :return:
        """

        order_book = self.get_Depth(coin)

        total_volume = 0.0
        current_price = 0.0

        for price, volume, timestamp in order_book[type]:
            current_price = price
            total_volume += volume
            if total_volume >= float(self.order_volume):
                break

        return float(current_price)


    def update_litecoins(self):
        """
        Updates all information on litecoin based on the coin ticker query
        :return:
        """

        self.litecoin_USD_ask = self.get_limit_price('asks', 'LTCUSD')
        self.litecoin_USD_bid = self.get_limit_price('bids', 'LTCUSD')


    def update_bitcoins(self):
        """
        Updates all bitcoin information based on the coin ticker query
        :return:
        """


        self.bitcoin_USD_ask = self.get_limit_price('asks', 'XBTUSD')
        self.bitcoin_USD_bid = self.get_limit_price('bids', 'XBTUSD')
        self.json = self.kraken.query_public('Ticker', {'pair': 'LTCUSD,XBTUSD,ETHUSD'})


    def update_ether(self):
        """
        Updates all ether information based on the coin ticker query
        :return:
        """

        self.ether_USD_ask = self.get_limit_price('asks', 'ETHUSD')
        self.ether_USD_bid = self.get_limit_price('bids', 'ETHUSD')