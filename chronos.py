# contains all short time data, immediate changes etc


import threading
import time
from collections import defaultdict
import krakenex
from tabulate import tabulate
from gdax_exchange.gdax_exchange import Gdax as coinbase
from gemini.client import Client
from gemini_exchange.gemini_exchange import Gemini as gemini
from kraken_exchange.kraken import Kraken as kraken
from poloniex import Poloniex
from poloniex_exchange.poloniex import Poloniex as polonx
from config_parsing import parse_config
from fake_transactions import FakeTransactions as fake_transactions
from chronos_logging.excel_logger import ExcelLogger
from chronos_logging.sms_logger import SmsLogger
from chronos_logging.logger import *
from spread_tracking import SpreadTracking
from collections import OrderedDict



class Chronos(object):
    def __init__(self):
        self.configs = defaultdict(dict)
        self.config = parse_config()
        set_log_filehandler()
        self.sms_log = SmsLogger(config=self.config)
        self.time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S%f')[:-3]
        self.krakenexchange = self.start_kraken_thread()
        self.geminiexchange = self.start_gemini_thread()
        self.coinbaseexchange = self.start_gdax_thread()
        self.poloniexexchange = self.start_poloniex_thread()
        self.growth_entry = float(self.config['chronos']['growth_entry'])
        self.spread_entry = float(self.config['chronos']['spread_entry'])
        self.growth_exit = float(self.config['chronos']['growth_exit'])
        self.spread_exit = float(self.config['chronos']['spread_exit'])
        self.max_array_size = 2
        self.book = None
        self.start_arbitrage_deamon(self.geminiexchange, self.coinbaseexchange, 'ether')
        self.tracker = []
        self.query_list = []
        if not os.path.exists('./results/excels/{}'.format(self.time)):
            os.makedirs('./results/excels/{}'.format(self.time))
        self.query_coin_data()



    def start_arbitrage_deamon(self, high_exchange, low_exchange, coin):
        """
        Starts deamon that tracks coin information
        :return: None
        """
        log.debug("Starting {0} and {1} log for {2}".format(high_exchange, low_exchange, coin))
        arbitrage_bot = threading.Thread(target=self.perform_litecoin_arbitrage_thread, args=(high_exchange,low_exchange, coin))
        arbitrage_bot.daemon = True
        arbitrage_bot.start()
        return

    def query_coin_data(self):
        """
        This is a print out to the console the realtime exchange data and spreads aggregated side by side
        :return:
        """
        time.sleep(30)
        while True:
            time.sleep(3)
            for tracker in self.tracker:
                exchanges = "{0}/{1}".format(tracker.short_exchange, tracker.long_exchange)
                self.query_list.append(OrderedDict([("Exchange", exchanges),
                                                    ("Coin", tracker.coin_type),
                                                    ("Short", tracker.short_coin),
                                                    ("Long", tracker.long_coin),
                                                    ("Spread", tracker.spread),
                                                    ("Growth Rate", tracker.growth_rate)]))

            print tabulate(self.query_list, headers='keys')
            print "\n"
            self.query_list = []


    def perform_litecoin_arbitrage_thread(self, high_exchange, low_exchange, coin):
        """
        Given two exchange objects this thread function will continually check for entry criteria
        between each exchange with both as the short and as the long
        :param exchangex:
        :param exchangey:
        :return:
        """
        #give time for the exchange threads to populate its data
        time.sleep(20)
        excel_log = ExcelLogger(high_exchange.name, low_exchange.name, self.time)
        excel_log1 = ExcelLogger(low_exchange.name, high_exchange.name, self.time)
        log.debug("Creating Excel loggers {0} and {1}".format(low_exchange.name, high_exchange.name))
        spread_tracker = SpreadTracking(self.max_array_size, high_exchange.name, low_exchange.name, coin)
        spread_tracker1 = SpreadTracking(self.max_array_size,low_exchange.name, high_exchange.name, coin)
        self.tracker.append(spread_tracker)
        self.tracker.append(spread_tracker1)
        while True:
            time.sleep(3)
            entry_check1 = self.check_for_entry_criteria(high_exchange,low_exchange, excel_log, spread_tracker, coin)
            entry_check2 = self.check_for_entry_criteria(low_exchange, high_exchange, excel_log1, spread_tracker1, coin)
            if entry_check1:
                # exchange x borrow lite coin, sell it,
                # buy exchange y
                # start check for exit loop
                #TODO This is where real transactions will be intitated depending on debug configuration
                #print 'Short sell on {0} and buy on {1} '.format(exchangex.name, exchangey.name)
                log.info("Entering REAL arbitrage short/buy for {0}/{1}".format(high_exchange.name, low_exchange.name))
                #self.do_fake_arbitrage(short_exchange=exchangex, long_exchange=exchangey, excel=excel_log, spread_tracker=spread_tracker, coin=coin)
                log.debug("{0} is lower exchange and ask price is {1}".format(low_exchange.name, low_exchange.ether_USD_ask))
                log.debug("{0} is higher exchange and bid price is {1}".format(high_exchange.name, high_exchange.ether_USD_bid))
                self.do_real_arbitrage(lower_exchange=low_exchange, higher_exchange=high_exchange, excel=excel_log,spread_tracker=spread_tracker, coin=coin)


            if entry_check2:
                # exchange x borrow lite coin, sell it,
                # buy exchange y
                # start check for exit loop
                #print 'Short sell on {0} and buy on {1} '.format(exchangey.name, exchangex.name)
                log.info("Entering REAL arbitrage buy/short for {0}/{1}".format(low_exchange.name, high_exchange.name))
                #self.do_fake_arbitrage(short_exchange=exchangey, long_exchange=exchangex, excel=excel_log1, spread_tracker=spread_tracker1, coin=coin)



    def wait_for_exit(self, exchange1, exchange2, excel, spread_tracker, coin):
        """
        Given two exchange objects and its spread tracker it determines,
        if the short exchange is ready to exit the spread
        :param exchange1: the short exchange in the spread
        :param exchange2: the long exchange in the spread
        :param excel:
        :param spread_tracker:
        :return:
        """
        while True:
            time.sleep(3)
            bid = getattr(exchange1, "{0}_USD_bid".format(coin))
            ask = getattr(exchange2, "{0}_USD_ask".format(coin))
            spread_tracker.get_spread(bid, ask)
            spread_tracker.add_spread_to_array()

            try:
                if len(spread_tracker.trailing_array) <= 1:
                    pass
                else:
                    spread_tracker.get_growth_rate()
            except:
                log.debug("Couldn't get growth rate")
                log.debug("Trailing array: {}".format(spread_tracker.trailing_array))

            string = '----{0}/{1}       ' + '{2}/{3}'.ljust(37) + '{4}%    {5}% \n'.ljust(5)
            #print string.format(exchange1.name,
                               # exchange2.name,
                               # exchange1.litecoin_USD_lasttrade,
                                #exchange2.litecoin_USD_lasttrade,
                                #exchange1.spread,
                                #exchange1.growth_rate)

            #excel.log_excel(exchange1.litecoin_USD_lasttrade,
             #               exchange2.litecoin_USD_lasttrade,
              #              spread_tracker.spread,
               #             spread_tracker.growth_rate)

            if spread_tracker.growth_rate <= self.growth_exit and spread_tracker.spread <= self.spread_exit:
                log.debug("Exiting arbitrage short/buy for {0}/{1}".format(exchange1.name, exchange2.name))
                return True
            else:
                continue


    def check_for_entry_criteria(self, exchange1, exchange2, excel, spread_tracker, coin):
        """
        Given a short exchange and a long exchange it determines if its ready to enter
        based on the spread and growth rate
        :param exchange1:
        :param exchange2:
        :param excel:
        :param spread_tracker:
        :return:
        """
        bid = getattr(exchange1, "{0}_USD_bid".format(coin))
        ask = getattr(exchange2, "{0}_USD_ask".format(coin))
        spread_tracker.get_spread(bid, ask)
        spread_tracker.add_spread_to_array()
        try:
            spread_tracker.get_growth_rate()
        except:
            log.debug( "Couldnt get growth rate")
        string = '----{0}/{1}       ' + '{2}/{3}'.ljust(37) + '{4}%    {5}% \n'.ljust(5)
        #print string.format(exchange1.name,
                            #exchange2.name,
                            #exchange1.litecoin_USD_lasttrade,
                            #exchange2.litecoin_USD_lasttrade,
                            #exchange1.spread,
                            #exchange1.growth_rate)

        #print 'Array: {0}\n'.format(exchange1.trailing_array)
        #excel.log_excel(exchange1.litecoin_USD_lasttrade,
         #               exchange2.litecoin_USD_lasttrade,
          #              spread_tracker.spread,
           #             spread_tracker.growth_rate)

        if spread_tracker.growth_rate >= self.growth_entry and spread_tracker.spread >= self.spread_entry:
            return True
        else:
            return False

    def do_real_arbitrage(self, lower_exchange, higher_exchange, excel, spread_tracker, coin):
        """
        Performs a real arbitrade on a given opportunity between two exchanges and performs
        real transactions by taking money from the lower exchange , sending it to the higher exchange,
        and selling it.
        :param short_exchange:
        :param long_exchange:
        :param excel:
        :param spread_tracker:
        :param coin:
        :return:
        """
        coins = {'ether':'ETH', 'bitcoin':'BTC', 'litecoin':'LTC'}
        print "Performing real arbitrage"
        log.debug("{0} price is {1}".format(lower_exchange.name, lower_exchange.ether_USD_ask))
        lower_exchange_transactions = lower_exchange.open_wallet()
        higher_exchange_transactions = higher_exchange.open_wallet()
        ask = getattr(lower_exchange, "{0}_USD_ask".format(coin))
        shares = float(self.config['chronos']['wallet_exposure']) / float(ask)
        shares = round(shares, int(self.config[lower_exchange.name]['round']))
        coin_id = coins[coin]
        print shares
        print self.config['chronos']['wallet_exposure']
        print self.config[lower_exchange.name][coin]
        #make sure the volume for the price is close to available
        current_price = lower_exchange.get_limit_price('asks', shares)
        print current_price
        bid = getattr(higher_exchange, "{0}_USD_bid".format(coin))
        spread_tracker.get_spread(bid, current_price)
        spread_tracker.add_spread_to_array()
        try:
            spread_tracker.get_growth_rate()
        except:
            log.debug("Couldnt get growth rate while arbitraging")

        if spread_tracker.growth_rate >= self.growth_entry and spread_tracker.spread >= self.spread_entry:
            pass
        else:
            return

        shares = float(self.config['chronos']['wallet_exposure']) / float(current_price)
        shares = round(shares, int(self.config[lower_exchange.name]['round']))

        print lower_exchange_transactions.buy(self.config[lower_exchange.name][coin], shares, current_price)
        # get id from this return?
        # add checking for exchange
        available = self.check_for_deposit(lower_exchange_transactions, coin_id, shares)
        log.debug("Account balance after 2 mins : {}".format(available))
        if available == 0:
            return
        self.sms_log.log_sms_informing(short_exchange_name=lower_exchange.name, long_exchange_name=higher_exchange.name)
        print lower_exchange_transactions.crypto_withdraw(available, coin_id, self.config[higher_exchange.name]["wallet_address"])
        # check wallet if money is in it to the equivalent of what was already in there
        higher_shares = self.check_for_transaction(higher_exchange_transactions, coin_id, shares)
        higher_shares = round(higher_shares, int(self.config[higher_exchange.name]['round']))
        last_digit = str(higher_shares)[-1]
        last_digit = int(last_digit) - 1
        higher_shares = float(str(higher_shares)[:-1] + str(last_digit))
        # when it is , sell it , calculate returns
        # get current price of exchange
        bid = getattr(higher_exchange, "{0}_USD_bid".format(coin))
        print higher_exchange_transactions.sell(ask, higher_shares, self.config[higher_exchange.name][coin+'id'])
        profit = (float(bid)*float(higher_shares)) - (float(shares)*float(ask))
        self.sms_log.log_sms(short_exchange_name=higher_exchange.name, long_exchange_name=lower_exchange.name, profit=profit)


    def check_for_transaction(self, wallet, coin, shares_coming):
        #get account of that coin, when its greater than what it is, sell that size

        available = wallet.get_account_information(coin)
        new_available = available
        shares = shares_coming/2
        available = available + shares
        while available >= new_available:
            time.sleep(4)
            new_available = wallet.get_account_information(coin)

        return new_available

    def check_for_deposit(self, wallet, coin, shares):
        new_available = wallet.get_account_information(coin)

        available = 0.0
        seconds = 0
        while new_available <= available:
            time.sleep(3)
            print new_available
            print available
            new_available = wallet.get_account_information(coin)
            seconds += 1
            if seconds >= 40:
                return 0

        return new_available


    def do_fake_arbitrage(self, short_exchange, long_exchange, excel, spread_tracker, coin):
        """
        Performs an arbitrage on a given opportunity between two exchanges and performs
        fake simulated transactions
        :param short_exchange:
        :param long_exchange:
        :param excel:
        :param spread_tracker:
        :return:
        """
        exchange_short = short_exchange.start_transaction(coin)
        exchange_long = long_exchange.start_transaction(coin)

        #TODO have this automatically happen when start transaction gets called through configurations
        exchange_short.short_sell = getattr(short_exchange, "{0}_USD_bid".format(coin))
        exchange_short.share_values = int(self.config['chronos']['wallet_exposure'])
        exchange_short.start_arbitrage()

        exchange_long.buy = getattr(long_exchange, "{0}_USD_ask".format(coin))
        exchange_long.share_values = int(self.config['chronos']['wallet_exposure'])
        exchange_long.start_arbitrage()

        #excel.log_excel_enter(short_shares=exchange_short.shares,
         #                     short_coin=short_exchange.litecoin_USD_lasttrade,
          #                    long_shares=exchange_long.shares,
           #                   long_coin=long_exchange.litecoin_USD_lasttrade)

        self.wait_for_exit(short_exchange, long_exchange, excel, spread_tracker, coin)

        exchange_short.buy_back_price = getattr(short_exchange, "{0}_USD_ask".format(coin))
        exchange_short.share_values = int(self.config['chronos']['wallet_exposure'])
        profit1 = exchange_short.end_arbitrage()

        exchange_long.sell_price = getattr(long_exchange, "{0}_USD_bid".format(coin))
        exchange_long.share_values = int(self.config['chronos']['wallet_exposure'])
        profit2 = exchange_long.end_arbitrage()
        total_profit = (float(profit1) + float(profit2))
        #excel.log_excel_exit(short_shares=exchange_short.new_shares,
           #                   short_coin=short_exchange.litecoin_USD_lasttrade,
            #                  long_shares=exchange_long.shares,
             #                 long_coin=long_exchange.litecoin_USD_lasttrade,
              #               profit=total_profit)


        #print "Profitited : {0}".format((float(profit1) + float(profit2)))
        log.debug('Bot has profitted ${0}'.format(total_profit))
        self.sms_log.log_sms(short_exchange_name=short_exchange.name, long_exchange_name=long_exchange.name, profit=total_profit)
        #voice.send_sms(6313971667, 'Profit of ${0} with {1} as short and {2} as long'.format(total_profit, short_exchange.name,long_exchange.name))


    ##################
    #Helper Functions#
    ##################

    def get_growth_rate(self, trailing_array):
        """
        Given an array of trailing spreads determine what the growth rate of the spreads are
        :param trailing_array: An array of spread that is filled by the arbitrage thread
        :return: the growth rate of the set of given values
        """
        if trailing_array <= 1:
            return 0
        else:
            return (trailing_array[len(trailing_array) - 1] / trailing_array[0]) ** (1 / float(len(trailing_array))) - 1

    def get_spread(self, short_coin, long_coin):
        """
        Give two values finds the percentage of difference between them
        :param short_coin: The coin that is expected to be the higher value
        :param long_coin: The coin that is expected to be the lower value
        :return: the spread represented as a %
        """

        return (((float(short_coin) - float(long_coin)) /
          float(short_coin)) * 100)

    def add_spread_to_array(self, spread, array):
        """
        Appends to a historical spread, if adding a value exceeds maximum it pops the first value off
        :param spread: the spread value that is being added represented as a %
        :param array: the array of spreads
        :return:
        """
        if len(array) + 1 > self.max_array_size and (spread != array[len(array)-1]):
            array.append(spread)
            array.pop(0)
            return
        if len(array) == 0:
            array.append(spread)
            return

        if spread == array[len(array)-1]:
            return
        else:
            array.append(spread)




    ##################
    #Exchange threads#
    ##################

    def start_kraken_thread(self):
        """
        Creates a Kraken exchange object which starts a thread updating its values every X seconds
        based on its exchanges limit restrictions
        :return:
        """

        kraken_api = krakenex.API()
        kraken_api.load_key(str(self.config['kraken']['key_path']))
        return kraken(fake_transactions=fake_transactions,
                      exchange_api=kraken_api,
                      ask=str(self.config['kraken']['ask']),
                      bid=str(self.config['kraken']['bid']),
                      last=str(self.config['kraken']['last']),
                      bitcoin=str(self.config['kraken']['bitcoin']),
                      litecoin=str(self.config['kraken']['litecoin']),
                      ether=str(self.config['kraken']['ether']))


    def start_gemini_thread(self):
        """
        Creates a Gemini exchange object which starts a thread updating its values every X seconds
        based on its exchanges limit restrictions
        :return:
        """
        gemini_api = Client('r6ZTeaUX1DFGm3IaaMgF', '22ykz6Cwe91HAkg1rGDVZ467Czsx')
        return gemini(client=gemini_api,
                      fake_transactions=fake_transactions,
                      ask=str(self.config['gemini']['ask']),
                      bid=str(self.config['gemini']['bid']),
                      last=str(self.config['gemini']['last']),
                      bitcoin=str(self.config['gemini']['bitcoin']),
                      ether=str(self.config['gemini']['ether']))


    def start_gdax_thread(self):
        """
        Creates a gdax exchange object which starts a thread updating its values every X seconds
        based on its exchanges limit restrictions
        :return:
        """



        return coinbase(fake_transactions=fake_transactions,
                        key=str(self.config['gdax']['key']),
                        passphrase=str(self.config['gdax']['passphrase']),
                        b64secret=str(self.config['gdax']['b64secret']),
                        ask=str(self.config['gdax']['ask']),
                        bid=str(self.config['gdax']['bid']),
                        last=str(self.config['gdax']['last']),
                        bitcoin=str(self.config['gdax']['bitcoin']),
                        litecoin=str(self.config['gdax']['litecoin']),
                        ether=str(self.config['gdax']['ether']))


    def start_poloniex_thread(self):
        """
        Creates a poloniex exchange object which starts a thread updating its values every X seconds
        based on its exchanges limit restrictions
        :return:
        """
        poloniex_api = Poloniex()
        return polonx(fake_transactions=fake_transactions,
                      exchange_api=poloniex_api,
                      ask=str(self.config['poloniex']['ask']),
                      bid=str(self.config['poloniex']['bid']),
                      last=str(self.config['poloniex']['last']),
                      bitcoin=str(self.config['poloniex']['bitcoin']),
                      litecoin=str(self.config['poloniex']['litecoin']),
                      ether=str(self.config['poloniex']['ether']))