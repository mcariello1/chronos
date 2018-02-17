
from data_query import GeminiCoinData as data_query
from transactions import Transactions as transactions

class Gemini(data_query):
    def __init__(self, client, fake_transactions, ask=None, bid=None, last=None, bitcoin=None, ether=None):
        super(Gemini, self).__init__(client, ask=ask,bid=bid, last=last, bitcoin=bitcoin,ether=ether)
        self.client = client
        self.trailing_array = []
        self.spread = 0
        self.valid_coins = ['bitcoin', 'ether']
        self.growth_rate = 0
        self.fake_transactions = fake_transactions

    def start_transaction(self, coin):
        """
        Starts fake transaction object for when needed to do fake arbitrage
        :return:
        """
        return self.fake_transactions(self.name, coin)

    def open_wallet(self):
        """
        Open wallet authentication for making transactions
        :return:
        """

        return transactions(self.client)

