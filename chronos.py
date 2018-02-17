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
        self.threads = []
        self.configs = defaultdict(dict)
        self.config = parse_config()
        set_log_filehandler()
        self.sms_log = SmsLogger(config=self.config)
        self.time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S%f')[:-3]
        self.krakenexchange = self.start_kraken_thread()
        self.geminiexchange = self.start_gemini_thread()
        self.coinbaseexchange = self.start_gdax_thread()
        #self.poloniexexchange = self.start_poloniex_thread()
        self.growth_entry = float(self.config['chronos']['growth_entry'])
        self.spread_entry = float(self.config['chronos']['spread_entry'])
        self.growth_exit = float(self.config['chronos']['growth_exit'])
        self.spread_exit = float(self.config['chronos']['spread_exit'])
        self.max_array_size = 2
        self.book = None
        self.start_arbitrage_deamon(self.geminiexchange, self.coinbaseexchange, 'ether', 'USD')
        self.start_arbitrage_deamon(self.coinbaseexchange, self.krakenexchange,  'ether', 'USD')
        self.start_arbitrage_deamon(self.geminiexchange, self.krakenexchange, 'ether', 'USD')
        self.start_arbitrage_deamon(self.coinbaseexchange, self.krakenexchange, 'litecoin', 'USD')
        self.disabled_exchanges=['gemini']
        self.tracker = []
        self.query_list = []
        if not os.path.exists('./results/excels/{}'.format(self.time)):
            os.makedirs('./results/excels/{}'.format(self.time))
        self.thread_killer()
        self.query_coin_data()
        self.refund = 0




    def start_arbitrage_deamon(self, high_exchange, low_exchange, coin):
        """
        Starts deamon that tracks coin information
        :return: None
        """
        log.debug("Starting {0} and {1} log for {2}".format(high_exchange, low_exchange, coin))
        arbitrage_bot = threading.Thread(target=self.perform_litecoin_arbitrage_thread, args=(high_exchange,low_exchange, coin))
        arbitrage_bot.daemon = True
        arbitrage_bot.start()
        self.threads.append(arbitrage_bot)
        return

    def start_refund_deamon(self, higher_exchange, lower_exchange, valid_coins):
        log.debug("Starting refund deamon {0} and {1} log for {2}".format(higher_exchange, lower_exchange, valid_coins))
        arbitrage_bot = threading.Thread(target=self.refund_account, args=(higher_exchange, lower_exchange, valid_coins))
        arbitrage_bot.daemon = True
        arbitrage_bot.start()
        self.threads.append(arbitrage_bot)
        return

    def thread_killer(self):
        thread_bot = threading.Thread(target=self.kill_threads, args=())
        thread_bot.daemon = True
        thread_bot.start()
        return

    def kill_threads(self):
        time.sleep(50)
        while True:
            time.sleep(1)
            for x in self.threads:
                if not x.isAlive():

                    x.join()


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
                                                    ("Spread w/fees", tracker.spread_with_fees),
                                                    ("Growth Rate", tracker.growth_rate)]))

            print tabulate(self.query_list, headers='keys')
            print "\n"
            self.query_list = []


    def perform_litecoin_arbitrage_thread(self, high_exchange, low_exchange, coin, base_currency):
        """
        Given two exchange objects this thread function will continually check for entry criteria
        between each exchange with both as the short and as the long
        :param exchangex:
        :param exchangey:
        :param base_currency:
        :return:
        """
        #give time for the exchange threads to populate its data
        time.sleep(20)
        coins = {'ether': 'ETH', 'bitcoin': 'BTC', 'litecoin': 'LTC'}

        coin_id = coins[coin]

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
                high = getattr(high_exchange, "{0}_USD_ask".format(coin))
                low = getattr(low_exchange, "{0}_USD_bid".format(coin))
                log.debug("{0} is lower exchange and bid price is {1}".format(low_exchange.name, low))
                log.debug("{0} is higher exchange and ask price is {1}".format(high_exchange.name, high))
                lower_exchange_transactions = low_exchange.open_wallet()
                cash = lower_exchange_transactions.get_account_information(base_currency)

                if cash >= float(self.config['chronos']['wallet_exposure']):
                    self.do_real_arbitrage(lower_exchange=low_exchange, higher_exchange=high_exchange, excel=excel_log,spread_tracker=spread_tracker, coin=coin, refund=True, base_currency=base_currency)


            if entry_check2:
                # exchange x borrow lite coin, sell it,
                # buy exchange y
                # start check for exit loop
                #print 'Short sell on {0} and buy on {1} '.format(exchangey.name, exchangex.name)
                log.info("Entering REAL arbitrage short/buy for {0}/{1}".format(low_exchange.name, high_exchange.name))
                # self.do_fake_arbitrage(short_exchange=exchangex, long_exchange=exchangey, excel=excel_log, spread_tracker=spread_tracker, coin=coin)
                high = getattr(high_exchange, "{0}_USD_bid".format(coin))
                low = getattr(low_exchange, "{0}_USD_ask".format(coin))
                log.debug("{0} is lower exchange and bid price is {1}".format(high_exchange.name, high))
                log.debug("{0} is higher exchange and ask price is {1}".format(low_exchange.name, low))
                higher_exchange_transactions = high_exchange.open_wallet()
                cash = higher_exchange_transactions.get_account_information(base_currency)
                if cash >= float(self.config['chronos']['wallet_exposure']):
                    self.do_real_arbitrage(lower_exchange=high_exchange, higher_exchange=low_exchange, excel=excel_log, spread_tracker=spread_tracker1, coin=coin, refund=True, base_currency=base_currency)


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
        # being were not shorting , may no longer be valid for now
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
        #should I calculate spread w/ fees included ?
        bid = getattr(exchange1, "{0}_USD_bid".format(coin))
        ask = getattr(exchange2, "{0}_USD_ask".format(coin))
        spread_tracker.get_spread(float(bid),
                                  float(ask),
                                  float(self.config[exchange1.name]['fees']),
                                  float(self.config[exchange2.name]['fees']),
                                  float(self.config[exchange2.name]['{0}_withdraw_fees'.format(coin)]),
                                  float(self.config['chronos']['wallet_exposure']))

        spread_tracker.add_spread_to_array()
        try:
            spread_tracker.get_growth_rate()
        except:
            log.debug("Couldnt get growth rate")
            log.debug("Trailing array: {}".format(spread_tracker.trailing_array))


        if spread_tracker.growth_rate >= self.growth_entry and spread_tracker.spread_with_fees >= self.spread_entry:
            return True
        else:
            return False

    def do_real_arbitrage(self, lower_exchange, higher_exchange, excel, spread_tracker, coin, refund, base_currency):
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

        coin_id = coins[coin]# need to add just first coinid not base
        coin_value = coin + '_' + base_currency
        print "Performing real arbitrage"

        ask = getattr(lower_exchange, "{0}_USD_ask".format(coin))
        log.debug("{0} price is {1}".format(lower_exchange.name, ask))
        #self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Spread was large enough, entering")
        # open wallets for making transactions
        lower_exchange_transactions = lower_exchange.open_wallet()
        higher_exchange_transactions = higher_exchange.open_wallet()
        # perform buy and get the updated ask and shares available to withdraw
        (available, ask) = self.arbitrage_buy(lower_exchange, lower_exchange_transactions, higher_exchange, higher_exchange_transactions, coin, coin_id, spread_tracker, refund, coin_value)
        # if the buy didnt go through , exit and and enter again when spread is open
        if available == 0:
            #self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Going back to checking")
            return 0
        self.sms_log.log_sms_informing(short_exchange_name=lower_exchange.name, long_exchange_name=higher_exchange.name)
        log.debug("Withdrawing {0} shares of {1} to {2}".format(available, coin_id, higher_exchange.name))

        response = lower_exchange_transactions.crypto_withdraw(amount=available, currency=coin_id, crypto_address=self.config[higher_exchange.name]["{0}_wallet_address".format(coin)], exchange_name=higher_exchange.name)
        log.debug(response)
        # check wallet if money is in it to the equivalent of what was already in there
        self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Checking for withdrawl")
        log.debug("Checking for transactions")
        higher_exchange.making_transaction = 1
        higher_shares = self.check_for_transaction(higher_exchange_transactions, coin_id, available)
        self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Starting sell")
        current_price = self.arbitrage_sell(lower_exchange, higher_exchange, higher_exchange_transactions, coin, coin_id, higher_shares, refund, base_currency, coin_value)
        profit = (float(current_price)*float(higher_shares)) - (float(available)*float(ask))
        self.sms_log.log_sms(short_exchange_name=higher_exchange.name, long_exchange_name=lower_exchange.name, profit=profit)
        if refund:
            log.debug("Attempting to refund account")
            #self.start_refund_deamon(higher_exchange=lower_exchange, lower_exchange=higher_exchange, valid_coins=lower_exchange.valid_coins)
            self.refund_account(higher_exchange=lower_exchange, lower_exchange=higher_exchange, valid_coins=higher_exchange.valid_coins)



    def check_for_transaction(self, wallet, coin, shares_coming):
        #get account of that coin, when its greater than what it is, sell that size
        # get available shares in wallet
        available = wallet.get_account_information(coin)
        new_available = available
        shares = float(shares_coming/2)
        available = available + shares
        #wait for new shares to come in
        while available >= new_available:
            time.sleep(4)
            print new_available
            print available
            new_available = wallet.get_account_information(coin)
            log.debug('Shares available: {}'.format(new_available))

        return new_available

    def check_for_deposit(self, wallet, coin, shares, available):
        #get available shares
        new_available = available
        shares = float(shares / 2)
        seconds = 0
        # wait for wallet to receive shares
        while new_available <= shares:
            time.sleep(4)
            print new_available
            print available
            new_available = wallet.get_account_information(coin)
            seconds += 1
            if seconds >= 5:
                return 0

        print new_available
        print available
        return new_available

    def check_for_withdraw(self, wallet, coin, available):
        #get available shares
        new_available = available
        last_available = available
        # once over 90% complete, return
        complete = int(self.config['chronos']['wallet_exposure']) * .9
        available = available + complete
        seconds = 0
        #wait for shares to be withdraw from account
        while new_available <= available:
            time.sleep(4)
            print new_available
            print available
            new_available = wallet.get_account_information(coin)

            seconds += 1
            if new_available != last_available:
                growing = True
            else:
                growing = False
            if seconds >= 5 and not growing:
                return 0
        return 1


    def arbitrage_buy(self, lower_exchange,lower_exchange_transactions, higher_exchange, higher_exchange_transactions, coin, coin_id, spread_tracker, refund, coin_value):

        ask = getattr(lower_exchange, "{0}_ask".format(coin_value))
        log.debug("{0} price is {1}".format(lower_exchange.name, ask))
        shares = float(self.config['chronos']['wallet_exposure']) / float(ask)
        shares = round(shares, int(self.config[lower_exchange.name]['round']))
        print shares
        print self.config['chronos']['wallet_exposure']
        print self.config[lower_exchange.name][coin]
        lower_exchange.making_transaction = 1

        # make sure the volume for the price is close to available, get price of coin @ top of orderbook
        current_price = lower_exchange.get_limit_price('bids', shares, self.config[lower_exchange.name][coin_value])
        print current_price
        self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Re-checking spread")

        bid = getattr(higher_exchange, "{0}_bid".format(coin_value))
        spread_tracker.get_spread(bid, current_price,
                                  float(self.config[higher_exchange.name]['fees']),
                                  float(self.config[lower_exchange.name]['fees']),
                                  float(self.config[higher_exchange.name]['{0}_withdraw_fees'.format(coin_value)]),
                                  float(self.config['chronos']['wallet_exposure']))

        spread_tracker.add_spread_to_array()
        try:
            spread_tracker.get_growth_rate()
        except:
            log.debug("Couldnt get growth rate while arbitraging")
            log.debug("Trailing array: {}".format(spread_tracker.trailing_array))

        if spread_tracker.growth_rate >= self.growth_entry and spread_tracker.spread_with_fees >= self.spread_entry:
            pass
        else:
            log.debug("Spread is no longer valid")

            lower_exchange.making_transaction = 0
            return (0 , 0)

        if not refund:
            current_price = current_price - .02
        else:
            current_price = current_price + .01
        current_price = round(current_price, 2)
        shares = float(self.config['chronos']['wallet_exposure']) / float(current_price)
        #round the shares to prpoer decimal #
        shares = round(shares, int(self.config[lower_exchange.name]['round']))
        #perform buy
        self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Buying")

        available = lower_exchange_transactions.get_account_information(coin_id)

        log.debug("Buying {0} shares @ {1}".format(shares, current_price))
        response = lower_exchange_transactions.buy(self.config[lower_exchange.name][coin_value], shares, current_price)
        # validate the buy was executed
        log.debug(response)
        self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Checking for deposit")
        log.debug("Checking if shares deposited")
        available = self.check_for_deposit(lower_exchange_transactions, coin_id, shares, available)
        log.debug("Account balance after 2 mins : {}".format(available))
        if available == 0:
            # if the order was never filled
            self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Cancelling order")
            lower_exchange_transactions.cancel_order(response)
            lower_exchange.making_transaction = 0
            return (available, 0)
        lower_exchange.making_transaction = 0
        return (available, current_price)


    def arbitrage_sell(self, lower_exchange, higher_exchange, higher_exchange_transactions, coin, coin_id, higher_shares, refund, base_currency, coin_value):

        # round down the last digit down rather than up
        higher_shares = round(higher_shares, int(self.config[higher_exchange.name]['round']))
        last_digit = str(higher_shares)[-1]
        last_digit = int(last_digit) - 1
        higher_shares = float(str(higher_shares)[:-1] + str(last_digit))
        # when it is , sell it , calculate returns
        # get current price of exchange
        current_price = higher_exchange.get_limit_price('bids', higher_shares, self.config[higher_exchange.name][coin_value])
        #get the amount of USD cash in wallet
        if not refund:
            current_price = current_price + .02
        else:
            current_price = current_price - .01
        current_price = round(current_price, 2)
        cash_available = higher_exchange_transactions.get_account_information(base_currency)
        #sell shares
        self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Selling")
        log.debug("Selling {0} shares @ {1}".format(higher_shares, current_price))
        response = higher_exchange_transactions.sell(current_price, higher_shares, self.config[higher_exchange.name][coin + 'id'])
        #validate the shares were sold and converted to USD
        log.debug(response)
        self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Checking sell off")
        log.debug("Checking if a widthdraw occured")
        available = self.check_for_withdraw(higher_exchange_transactions, base_currency, cash_available)
        log.debug("Account balance after 2 mins : {}".format(available))
        #value = 0
        while available == 0:
            self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Sell did not work")
            '''
            if value == 10:
                # if taking too long to perform limit, make limit price @ top of order book and sell with fee
                higher_exchange_transactions.cancel_order(response)
                current_price = higher_exchange.get_limit_price('asks', higher_shares,self.config[lower_exchange.name][coin])
                cash_available = higher_exchange_transactions.get_account_information('USD')
                response = higher_exchange_transactions.sell(current_price, higher_shares, self.config[higher_exchange.name][coin + 'id'])
                available = self.check_for_withdraw(higher_exchange_transactions, 'USD',  cash_available)
                value = 0
            else:
            '''
            # if the order was never filled try again
            higher_exchange_transactions.cancel_order(response)                     #need to add specific coin/basecurrency id
            current_price = higher_exchange.get_limit_price('asks', higher_shares, self.config[higher_exchange.name][coin_value])
            if not refund:
                current_price = current_price + .02
            else:
                current_price = current_price - .01
            current_price = round(current_price, 2)
            cash_available = higher_exchange_transactions.get_account_information(base_currency)
            log.debug("Selling {0} shares @ {1}".format(higher_shares, current_price))   #need to add specific coin/basecurrency id
            response = higher_exchange_transactions.sell(current_price, higher_shares, self.config[higher_exchange.name][coin_value + 'id'])
            log.debug("Checking if a widthdraw occured")
            available = self.check_for_withdraw(higher_exchange_transactions, base_currency, cash_available)
            #value += 1

        self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Sold")
        higher_exchange.making_transaction = 0

        return current_price

    def refund_account(self, higher_exchange, lower_exchange, valid_coins):
        """
        After arbitrage has completed , need to refund account without losing profit.
        :param higher_exchange:
        :param lower_exchange:
        :param coin_used:
        :return:
        """
        # Find a transfer that will at the very least, cost nothing.
        # check the spreads with different fees
        # buy coin with best profit or no loss spread other than coin used
        # withdraw it
        # cash out

        # Have this function execute as a thread, also add functionality to not execute the arbitrage if that is
        #not have enough money in the account
        coin_dict = dict()
        coin_spread = dict()
        no_spread = True
        log.debug("Refunding account")
        refund = "(refund #{0})".format(self.refund)
        self.refund += 1
        ether_tracker = SpreadTracking(self.max_array_size, higher_exchange.name + refund, lower_exchange.name+ refund, 'ether')
        bitcoin_tracker = SpreadTracking(self.max_array_size, higher_exchange.name+ refund, lower_exchange.name+ refund, 'bitcoin')
        litecoin_tracker = SpreadTracking(self.max_array_size, higher_exchange.name+ refund, lower_exchange.name+ refund, 'litecoin')
        self.tracker.append(ether_tracker)
        self.tracker.append(bitcoin_tracker)
        self.tracker.append(litecoin_tracker)
        tracker_dict = {'ether': ether_tracker, 'bitcoin': bitcoin_tracker, 'litecoin': litecoin_tracker}
        while no_spread:
            time.sleep(3)
            for coin in valid_coins:
                bid = getattr(lower_exchange, "{0}_USD_bid".format(coin))
                ask = getattr(higher_exchange, "{0}_USD_ask".format(coin))
                spread_tracker = tracker_dict[coin]
                coin_dict[coin] = spread_tracker.get_spread(float(ask),
                                                            float(bid),
                                                            float(self.config[higher_exchange.name]['fees']),
                                                            float(self.config[lower_exchange.name]['fees']),
                                                            float(self.config[lower_exchange.name]['{0}_withdraw_fees'.format(coin)]),
                                                            float(self.config['chronos']['wallet_exposure']))
                spread_tracker.add_spread_to_array()
                try:
                    spread_tracker.get_growth_rate()
                except:
                    log.debug("Couldnt get growth rate")
                    log.debug("Trailing array: {}".format(spread_tracker.trailing_array))

                if spread_tracker.growth_rate >= self.growth_entry and spread_tracker.spread_with_fees >= .1:
                    coin_spread[coin] = spread_tracker.spread_with_fees
                else:
                    pass

            if len(coin_spread) > 0:
                log.debug("Spread has opened entering market")
                for x in self.tracker:
                    if refund in x.short_exchange:
                        self.tracker.remove(x)
                self.sms_log.log_sms_test(higher_exchange, lower_exchange, "Refund spread opened")
                coin_spreads = sorted(coin_spread.iteritems(), key=lambda (k,v): (v,k))
                coin, spread = coin_spreads[-1]
                log.debug("Entering with {0} coin with spread {1}".format(coin, spread))
                response = self.do_real_arbitrage(lower_exchange=lower_exchange, higher_exchange=higher_exchange, excel=[], spread_tracker=spread_tracker, coin=coin,refund=False)
                if response:
                    return
                coin_spread = dict()

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
    #################3

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
