import threading
import time

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
        while self.making_transaction == 0:
            time.sleep(self.request_duration)
            try:
                #self.exchange.update_bitcoins()
                self.exchange.update_ether()
                #self.exchange.update_litecoins()
            except:
                print 'Couldnt update coins'
