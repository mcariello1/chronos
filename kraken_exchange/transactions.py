
class Transactions(object):
    def __init__(self, client):
        self.auth_client = client


    def buy(self, symbol, amount, price):
        '''
        Buys on the gdax exchange
        :param price: current price of coin
        :param amount: volume you want to add
        :param symbol: XLTCZUSD, XXBTZUSD, XETHZUSD
        :return:
        '''

        args = {'pair': symbol, 'type': 'buy', 'ordertype': 'limit', 'price': price, 'volume': amount}
        json = self.auth_client.query_private('AddOrder', args)
        return json

    def sell(self, price, amount, symbol ):
        '''
        Sells on the gdax exchange
        :param price:
        :param size:
        :param product_id:
        :return:
        '''

        args = {'pair': symbol, 'type': 'sell', 'ordertype': 'limit', 'price': price, 'volume': amount}
        json = self.auth_client.query_private('AddOrder', args)
        return json


    def crypto_withdraw(self, amount,currency, crypto_address, exchange_name):
        '''
        Withdraws currency on the gdax exchange to another wallet
        :param amount:
        :param currency:
        :param crypto_address:
        :return:
        '''
        list = {'ETHgdax': 'gdax_ether',
                'ETHgemini':'gemini_ether',
                'LTCgdax':'gdax_litecoin',
                'LTCgemini':'gemini_litcoin',
                'BTCgdax':'gdax_bitcoin',
                'BTCgemini': 'gemini_bitcoin'}
        key = currency+exchange_name
        address = list[key]
        json = self.auth_client.query_private('Withdraw', {'asset': currency, 'key': address, 'amount': amount})
        return json

    def get_account_information(self, coin):
        """
        Gets account information for a particular coin
        :param coin:
        :return:
        """
        coin_id = {'ETH': 'XETH', 'LTC': 'XLTC', 'USD':'ZUSD'}
        coin_tag = coin_id[coin]
        accounts = self.auth_client.query_private('Balance')
        accounts = accounts['result']
        if coin_tag in accounts:
            return float(accounts[coin_tag])
        return 0

    def cancel_order(self, response):

        id = response['result']['txid'][0]

        self.auth_client.query_private('CancelOrder', {'txid': id})

