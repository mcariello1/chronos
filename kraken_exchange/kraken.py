from data_query import KrakenCoinData as data_query
from transactions import Transactions as transactions


class Kraken(data_query):
    def __init__(self, fake_transactions, exchange_api, ask=None, bid=None, last=None, bitcoin=None, litecoin=None, ether=None):
        super(Kraken, self).__init__(exchange_api=exchange_api, ask=ask,bid=bid, last=last, bitcoin=bitcoin,litecoin=litecoin,ether=ether)
        #TODO erase all this not needed
        self.trailing_array = []
        self.spread = 0
        self.trailing_array1 = []
        self.trailing_array2 = []
        self.trailing_array3 = []
        self.trailing_array4 = []
        self.spread1 = 0
        self.spread2 = 0
        self.spread3 = 0
        self.spread4 = 0
        self.growth_rate = 0
        self.growth_rate1 = 0
        self.growth_rate2 = 0
        self.growth_rate3 = 0
        self.growth_rate4 = 0
        self.fake_transactions = fake_transactions
        self.client = exchange_api

    def start_transaction(self, coin):
        """
        Creates a fake transaction object for doing a fake arbitrage transaction
        :return:
        """

        return self.fake_transactions(self.name, coin)

    def open_wallet(self):
        """
        Open wallet authentication for making transactions
        :return:
        """

        return transactions(self.client)