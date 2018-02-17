from common_data_query import CommonCoinData
REQUEST_DURATION = 3
LTCUSD = 'XLTCZUSD'
XBTUSD = 'XXBTZUSD'
ETHUSD = 'XETHZUSD'


class KrakenCoinData(CommonCoinData):
    def __init__(self, exchange_api, ask=None, bid=None, last=None, bitcoin=None, litecoin=None, ether=None):
        self.kraken = exchange_api
        self.litecoin_USD_bid = 0.0
        self.litecoin_USD_ask = 0.0
        self.litecoin_USD_lasttrade = 0.0
        self.ether_USD_bid = 0.0
        self.ether_USD_ask = 0.0
        self.ether_USD_lasttrade = 0.0
        self.bitcoin_USD_bid = 0.0
        self.bitcoin_USD_ask = 0.0
        self.bitcoin_USD_lasttrade = 0.0
        self.litecoin_key = litecoin
        self.bitcoin_key = bitcoin
        self.ether_key = ether
        self.ask_key = ask
        self.bid_key = bid
        self.making_transaction = 0
        self.name = 'kraken'
        self.order_volume = None
        self.keys = {'LTCUSD': LTCUSD, 'XBTUSD': XBTUSD, 'ETHUSD': ETHUSD}
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

        return float(current_price) - 0.05

    def get_coin_ticker_information(self, result, coin, key, value_location):
        """
        Gets all data information for litecoin, bitcoin, and ether
        :param result: the entire json
        :param coin: the coin to be searched
        :param key: the key for the specific value for that coin wanted
        :param value_location: the location of that value
        :return:
        """
        return result[coin][key][value_location]

    def update_litecoins(self):
        """
        Updates all information on litecoin based on the coin ticker query
        :return:
        """
        json = self.kraken.query_public('Ticker', {'pair': 'LTCUSD,XBTUSD,ETHUSD'})
        self.litecoin_USD_ask = float(self.get_coin_ticker_information(result=json['result'],
                                                                 coin=self.litecoin_key,
                                                                 key=self.ask_key,
                                                                 value_location=0))
        self.litecoin_USD_bid = float(self.get_coin_ticker_information(result=json['result'],
                                                                 coin=self.litecoin_key,
                                                                 key=self.bid_key,
                                                                 value_location=0))


    def update_bitcoins(self):
        """
        Updates all bitcoin information based on the coin ticker query
        :return:
        """
        json = self.kraken.query_public('Ticker', {'pair': 'LTCUSD,XBTUSD,ETHUSD'})
        self.bitcoin_USD_ask = float(self.get_coin_ticker_information(result=json['result'],
                                                                coin=self.bitcoin_key,
                                                                key=self.ask_key,
                                                                value_location=0))
        self.bitcoin_USD_bid = float(self.get_coin_ticker_information(result=json['result'],
                                                                coin=self.bitcoin_key,
                                                                key=self.bid_key,
                                                                value_location=0))


    def update_ether(self):
        """
        Updates all ether information based on the coin ticker query
        :return:
        """
        json = self.kraken.query_public('Ticker', {'pair': 'LTCUSD,XBTUSD,ETHUSD'})
        self.ether_USD_ask = float(self.get_coin_ticker_information(result=json['result'],
                                                              coin=self.ether_key,
                                                              key=self.ask_key,
                                                              value_location=0))
        self.ether_USD_bid = float(self.get_coin_ticker_information(result=json['result'],
                                                              coin=self.ether_key,
                                                              key=self.bid_key,
                                                              value_location=0))
