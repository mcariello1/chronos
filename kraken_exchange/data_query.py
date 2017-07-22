from common_data_query import CommonCoinData

REQUEST_DURATION = 3

class KrakenCoinData(CommonCoinData):
    def __init__(self, exchange_api, ask=None, bid=None, last=None, bitcoin=None, litecoin=None, ether=None):
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
        self.ask_key = ask
        self.bid_key = bid
        self.last_key = last
        self.value_location = 0
        self.litecoin_key = litecoin
        self.bitcoin_key = bitcoin
        self.ether_key = ether
        self.name = 'kraken_exchange'
        self.json = self.kraken.query_public('Ticker', {'pair': 'LTCUSD,XBTUSD,ETHUSD'})
        super(KrakenCoinData, self).__init__(exchange=self, request_duration=REQUEST_DURATION)


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
        self.litecoin_USD_ask = self.get_coin_ticker_information(result=self.json['result'],
                                                                 coin=self.litecoin_key,
                                                                 key=self.ask_key,
                                                                 value_location=0)
        self.litecoin_USD_bid = self.get_coin_ticker_information(result=self.json['result'],
                                                                 coin=self.litecoin_key,
                                                                 key=self.bid_key,
                                                                 value_location=0)
        self.litecoin_USD_lasttrade = self.get_coin_ticker_information(result=self.json['result'],
                                                                       coin=self.litecoin_key,
                                                                       key=self.last_key,
                                                                       value_location=0)
    def update_bitcoins(self):
        """
        Updates all bitcoin information based on the coin ticker query
        :return:
        """
        self.bitcoin_USD_ask = self.get_coin_ticker_information(result=self.json['result'],
                                                                 coin=self.bitcoin_key,
                                                                 key=self.ask_key,
                                                                 value_location=0)
        self.bitcoin_USD_bid = self.get_coin_ticker_information(result=self.json['result'],
                                                                 coin=self.bitcoin_key,
                                                                 key=self.bid_key,
                                                                 value_location=0)
        self.bitcoin_USD_lasttrade = self.get_coin_ticker_information(result=self.json['result'],
                                                                       coin=self.bitcoin_key,
                                                                       key=self.last_key,
                                                                       value_location=0)
    def update_ether(self):
        """
        Updates all ether information based on the coin ticker query
        :return:
        """
        self.ether_USD_ask = self.get_coin_ticker_information(result=self.json['result'],
                                                                coin=self.ether_key,
                                                                key=self.ask_key,
                                                                value_location=0)
        self.ether_USD_bid = self.get_coin_ticker_information(result=self.json['result'],
                                                                coin=self.ether_key,
                                                                key=self.bid_key,
                                                                value_location=0)

        self.ether_USD_lasttrade = self.get_coin_ticker_information(result=self.json['result'],
                                                                      coin=self.ether_key,
                                                                      key=self.last_key,
                                                                      value_location=0)


