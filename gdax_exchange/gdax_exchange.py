
from data_query import GdaxCoinData as data_query
from transactions import Transactions as transactions

class Gdax(data_query):
    def __init__(self,fake_transactions, key, passphrase, b64secret, ask=None, bid=None, last=None, bitcoin=None, litecoin=None, ether=None):
        super(Gdax, self).__init__(ask=ask,bid=bid, last=last, bitcoin=bitcoin,litecoin=litecoin,ether=ether)
        self.trailing_array = []
        self.spread = 0
        self.growth_rate = 0
        self.fake_transactions = fake_transactions
        self.key = key
        self.valid_coins = ['bitcoin', 'ether', 'litecoin']
        self.passphrase = passphrase
        self.b64secret = b64secret

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

        return transactions(self.key, self.passphrase, self.b64secret)

