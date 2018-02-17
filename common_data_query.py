import threading
import time
from chronos_logging.logger import *

class CommonCoinData(object):
    def __init__(self, exchange, request_duration):
        self.making_transaction = 0
        self.exchange = exchange
        self.request_duration = request_duration
        self.start_client_deamon()

    def start_client_deamon(self):
        """
        Starts deamon that tracks coin information
        :return: None
        """
        self.client_query = threading.Thread(target=self.query_public_coin_values, args=())
        self.client_query.daemon = True
        self.client_query.start()


    def query_public_coin_values(self):
        """
        Queries and updates all coin fields
        :return:
        """
        print 'started {0} thread'.format(self.exchange.name)
        while True:
            if self.making_transaction == 0:
                try:
                    coins = ['litecoin', 'ether', 'bitcoin']
                    self.exchange.update_coins(coins)
                except Exception as e:
                    log.debug(e)
                    log.debug('Couldnt update coins for {0}'.format(self.exchange.name))
                time.sleep(self.request_duration)
            else:
                time.sleep(self.request_duration - 2)
                log.debug("Transaction in progress, querying turned off for {0}".format(self.exchange.name))