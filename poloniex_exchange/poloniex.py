
from data_query import PoloniexCoinData as data_query


class Poloniex(data_query):
    def __init__(self, fake_transactions, exchange_api, ask=None, bid=None, last=None, bitcoin=None, litecoin=None, ether=None):
        super(Poloniex, self).__init__(exchange_api=exchange_api,ask=ask,bid=bid, last=last, bitcoin=bitcoin,litecoin=litecoin,ether=ether)
        self.trailing_array = []
        self.spread = 0
        self.growth_rate = 0
        self.fake_transactions = fake_transactions

    def start_transaction(self):
        """
        Creates fake transaction object when transaction is needed to be made
        :return:
        """
        return self.fake_transactions(self.name)