import time
REQUEST_DURATION = 3
class Transactions(object):
    def __init__(self, client):
        self.auth_client = client
        self.client_id = str(time.time())

    def buy(self, symbol, amount, price):
        '''
        Buys on the gdax exchange
        :param price:
        :param size:
        :param product_id:
        :return:
        '''

        json = self.auth_client.new_order(self.client_id, symbol, amount, price, "buy", "exchange limit", None)
        return json

    def sell(self, price, amount, symbol ):
        '''
        Sells on the gdax exchange
        :param price:
        :param size:
        :param product_id:
        :return:
        '''

        json = self.auth_client.new_order(self.client_id, symbol, amount, price, "sell", "exchange limit", None)
        return json

    def crypto_withdraw(self, currency, crypto_address, amount):
        '''
        Withdraws currency on the gdax exchange to another wallet
        :param amount:
        :param currency:
        :param crypto_address:
        :return:
        '''

        json = self.auth_client.withdraw_crypto(amount=amount, currency=currency, crypto_address=crypto_address)
        return json

    def get_account_information(self, coin):
        """
               Gets account information for a particular coin
               :param coin:
               :return:
               """
        accounts = self.auth_client.get_balance()
        for account in accounts:
            if coin in account['currency']:
                return float(account['available'])

        return None

