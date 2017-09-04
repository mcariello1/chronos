
from data_query import GdaxCoinData as data_query

class Gdax(data_query):
    def __init__(self,fake_transactions, ask=None, bid=None, last=None, bitcoin=None, litecoin=None, ether=None):
        super(Gdax, self).__init__(ask=ask,bid=bid, last=last, bitcoin=bitcoin,litecoin=litecoin,ether=ether)
        self.trailing_array = []
        self.spread = 0
        self.growth_rate = 0
        self.fake_transactions = fake_transactions

    def start_transaction(self, coin):
        """
        Starts fake transaction object for when needed to do fake arbitrage
        :return:
        """
        return self.fake_transactions(self.name, coin)
