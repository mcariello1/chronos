from common_data_query import CommonCoinData
import gdax

REQUEST_DURATION = 3

class Transactions(object):
    def __init__(self, key, passphrase, b64secret):
        self.auth_client = gdax.AuthenticatedClient(key, b64secret, passphrase)# fix this



    def buy(self,  product_id, size, price):
        '''
        Buys on the gdax exchange
        :param price:
        :param size:
        :param product_id:
        :return:
        '''

        json = self.auth_client.buy(price=price, size=size, product_id=product_id)
        return json

    def sell(self, price, size, product_id):
        '''
        Sells on the gdax exchange
        :param price:
        :param size:
        :param product_id:
        :return:
        '''

        json = self.auth_client.sell(price=price, size=size, product_id=product_id)
        return json

    def crypto_withdraw(self, amount, currency, crypto_address, exchange_name):
        '''
        Withdraws currency on the gdax exchange to another wallet
        :param amount:
        :param currency:
        :param crypto_address:
        :return:
        '''

        json = self.auth_client.crypto_withdraw(amount=amount, currency=currency, crypto_address=crypto_address)
        return json

    def get_account_information(self, coin):

        """
        Gets account information for a particular coin
        :param coin:
        :return:
        """

        accounts = self.auth_client.get_accounts()
        for account in accounts:
            if coin in account['currency']:
                return float(account['available'])

        return 0

    def cancel_order(self, response):


        self.auth_client.cancel_order(response['id'])


