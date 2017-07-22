from data_query import BtceCoinData as data_query

class Btce(data_query):
    def __init__(self, fake_transactions, exchange_api,exchange_info, bitcoin=None, litecoin=None, ether=None):
        super(Btce, self).__init__(exchange_api=exchange_api, exchange_info=exchange_info,bitcoin=bitcoin,litecoin=litecoin,ether=ether)
        self.trailing_array = []
        self.spread = 0
        self.growth_rate = 0
        self.fake_transactions = fake_transactions
    def start_transaction(self):
        return self.fake_transactions(self.name)