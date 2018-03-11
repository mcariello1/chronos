
from datetime import datetime
from chronos_logging.logger import log
import time
import threading

class SpreadTracking(object):
    def __init__(self, max_array, short_exchange, long_exchange, coin):
        self.max_array_size = max_array
        self.spread = 0.0
        self.spread_with_fees = 0.0
        self.trailing_array = []
        self.growth_rate = 0
        self.short_exchange = short_exchange
        self.long_exchange = long_exchange
        self.short_coin = 0
        self.long_coin = 0
        self.coin_type = coin
        self.start_tracker_deamon()

    def start_tracker_deamon(self):
        """
        Starts deamon that tracks coin information
        :return: None
        """
        arbitrage_bot = threading.Thread(target=self.track_spreads, args=())
        arbitrage_bot.daemon = True
        arbitrage_bot.start()
        return

    def get_growth_rate(self):
        """
        Given an array of trailing spreads determine what the growth rate of the spreads are
        :param trailing_array: An array of spread that is filled by the arbitrage thread
        :return: the growth rate of the set of given values
        """
        if self.trailing_array <= 1:
            return 0
        else:
            growth_array = [self.trailing_array[0], self.trailing_array[-1]]
            growth = [100 * (b - a) / a for a, b in zip(growth_array[::1], growth_array[1::1])]
            self.growth_rate = growth[0]

    def get_spread(self, short_coin, long_coin, short_fees, long_fees, withdraw_fees, investment):
        """
        Give two values finds the percentage of difference between them
        :param short_coin: The coin that is expected to be the higher value
        :param long_coin: The coin that is expected to be the lower value
        :return: the spread represented as a %
        """
        self.short_coin = short_coin
        self.long_coin = long_coin
        self.spread= (((float(short_coin) - float(long_coin)) /
          float(short_coin)) * 100)

        self.get_spread_with_fees(short_coin, long_coin, short_fees, long_fees, withdraw_fees, investment)

    def get_spread_with_fees(self, short_coin, long_coin, short_fees, long_fees, withdraw_fees, investment):
        self.short_coin = short_coin
        self.long_coin = long_coin
        investment_with_fees = (investment - (investment*long_fees)) - (float(withdraw_fees) * float(long_coin))
        shares_with_fees = investment_with_fees/long_coin
        profit_no_fees = float(shares_with_fees) * float(short_coin)
        return_with_fees = profit_no_fees - (profit_no_fees*short_fees)

        self.spread_with_fees = (((float(return_with_fees) - float(investment)) /
                        float(return_with_fees)) * 100)

    def add_spread_to_array(self):
        """
        Appends to a historical spread, if adding a value exceeds maximum it pops the first value off
        :param spread: the spread value that is being added represented as a %
        :param array: the array of spreads
        :return:
        """
        if self.spread ==0:
            return
        if len(self.trailing_array) + 1 > self.max_array_size and (self.spread != self.trailing_array[len(self.trailing_array)-1]):
            self.trailing_array.append(self.spread)
            self.trailing_array.pop(0)
            return
        if len(self.trailing_array) == 0:
            self.trailing_array.append(self.spread)
            return

        if self.spread == self.trailing_array[len(self.trailing_array)-1]:
            return
        else:
            self.trailing_array.append(self.spread)
    def track_spreads(self):
        # you want to track between certain price points and get its max
        # when it goes above the bracket all the time accrued gets added
        # during the exchange you are recording each change with time, values, timestamps
        # when it closes you print the results

        accrued_data = []

        first_spread_start = None
        medium_spread_start = None
        large_spread_start = None
        xlarge_spread_start = None
        spread_times = {1: 0, 2: 0, 3: 0, 4: 0}
        start_time = None
        real_start_time = None
        time_holder = {1: None, 2: None, 3: None}
        max = 0
        while True:
            time.sleep(5)
            if self.spread_with_fees > 0.14 and self.spread_with_fees < 0.5:
                real_start_time = datetime.utcnow()
                if not start_time:
                    start_time = datetime.utcnow()
                accrued_data.append((datetime.utcnow(), self.spread_with_fees))

            if self.spread_with_fees > max:
                max = self.spread_with_fees

            if self.spread_with_fees >= .5 and self.spread_with_fees < .8:

                if not real_start_time:
                    real_start_time = datetime.utcnow()
                if not medium_spread_start:
                    medium_spread_start = datetime.utcnow()

                    time_holder[1] = start_time
                    time_holder[3] = large_spread_start
                    time_holder[4] = xlarge_spread_start
                    start_time = None
                    large_spread_start = None
                    xlarge_spread_start = None
                    for x in time_holder:
                        if time_holder[x]:
                            end_time = datetime.utcnow()
                            length = end_time - time_holder[x]
                            length = length.total_seconds() / 60
                            spread_times[x] = spread_times[x] + length

                            time_holder[x] = None

                accrued_data.append((datetime.utcnow(), self.spread_with_fees))

            if self.spread_with_fees >= .8 and self.spread_with_fees < 1.0:

                if not real_start_time:
                    real_start_time = datetime.utcnow()
                if not large_spread_start:
                    large_spread_start = datetime.utcnow()
                    time_holder[1] = start_time
                    time_holder[2] = medium_spread_start
                    time_holder[4] = xlarge_spread_start
                    start_time = None
                    medium_spread_start = None
                    xlarge_spread_start = None
                    for x in time_holder:
                        if time_holder[x]:
                            end_time = datetime.utcnow()
                            length = end_time - time_holder[x]
                            length = length.total_seconds() / 60
                            spread_times[x] = spread_times[x] + length

                            time_holder[x] = None

                accrued_data.append((datetime.utcnow(), self.spread_with_fees))

            if self.spread_with_fees >= 1.0:

                if not real_start_time:
                    real_start_time = datetime.utcnow()
                if not xlarge_spread_start:
                    xlarge_spread_start = datetime.utcnow()

                    time_holder[1] = start_time
                    time_holder[2] = medium_spread_start
                    time_holder[3] = large_spread_start
                    start_time = None
                    medium_spread_start = None
                    large_spread_start = None
                    for x in time_holder:
                        if time_holder[x]:
                            end_time = datetime.utcnow()
                            length = end_time - time_holder[x]
                            length = length.total_seconds() / 60
                            spread_times[x] = spread_times[x] + length

                            time_holder[x] = None

                accrued_data.append((datetime.utcnow(), self.spread_with_fees))

            if real_start_time and self.spread_with_fees < 0.13:
                time_holder[1] = start_time
                time_holder[2] = medium_spread_start
                time_holder[3] = large_spread_start
                time_holder[4] = xlarge_spread_start
                start_time = None
                medium_spread_start = None
                large_spread_start = None
                xlarge_spread_start = None
                for x in time_holder:
                    if time_holder[x]:
                        end_time = datetime.utcnow()
                        length = end_time - time_holder[x]
                        length = length.total_seconds() / 60
                        spread_times[x] = spread_times[x] + length
                        time_holder[x] = None
                end_time = datetime.utcnow()
                length = end_time - real_start_time
                length = length.total_seconds() / 60
                log.debug("{0}/{1}".format(self.short_exchange, self.long_exchange))
                log.debug("Max Spread: {0}% Minutes: {1}\n".format(max, length))
                spread_dict = {1: '.1% -.4%', 2: '.5% - .7%', 3: '.8%-.9%', 4: '> 1%'}

                log.debug("Spread times: {0} : {1} , {2} : {3} , {4} : {5}, {6} : {7}".format(spread_dict[1],
                                                                                              spread_times[1],
                                                                                              spread_dict[2],
                                                                                              spread_times[2],
                                                                                              spread_dict[3],
                                                                                              spread_times[3],
                                                                                              spread_dict[4],
                                                                                              spread_times[4]))

                log.debug("Values: {} \n".format(accrued_data))

                accrued_data = []

                max = 0
                end_time = None

                spread_times = {1: 0, 2: 0, 3: 0, 4: 0}
                real_start_time = None

    '''
    def track_spreads(self):
        # you want to track between certain price points and get its max
        # when it goes above the bracket all the time accrued gets added
        # during the exchange you are recording each change with time, values, timestamps
        # when it closes you print the results

        accrued_data = []
        first_spread_data = []
        second_spread_data = []
        third_spread_data = []
        first_spread_start = None
        second_spread_start = None
        third_spread_start = None
        spread_times = {1:0, 2:0, 3:0, 4:0}
        start_time = None
        max = 0
        while True:
            time.sleep(5)
	    print self.spread_with_fees
            if self.spread_with_fees > 0.1 and self.spread_with_fees < 0.5:
		log.debug('Tracking spreads')
                if not start_time:
                    start_time = datetime.utcnow()
                if start_time:
                    end_time = datetime.utcnow()
                    length = end_time - start_time
                    length = length.total_seconds() / 60
                    spread_times[1] = length
                accrued_data.append((datetime.utcnow(), self.spread_with_fees))

            if self.spread_with_fees > max:
                max = self.spread_with_fees

            if self.spread_with_fees >= .5 and self.spread_with_fees < .8:
                log.debug("Real spread opened")
		if not start_time:
                    first_spread_start = datetime.utcnow()
                if first_spread_start:
                    end_time = datetime.utcnow()
                    length = end_time - first_spread_start
                    length = length.total_seconds() / 60
                    spread_times[2] = length

                accrued_data.append((datetime.utcnow(), self.spread_with_fees))

            if self.spread_with_fees >= .8 and self.spread_with_fees < 1.0:
                if not second_spread_start:
                    second_spread_start = datetime.utcnow()
                if second_spread_start:
                    end_time = datetime.utcnow()
                    length = end_time - second_spread_start
                    length = length.total_seconds() / 60
                    spread_times[3] = length

                accrued_data.append((datetime.utcnow(), self.spread_with_fees))


            if self.spread_with_fees >= 1.0:
                if not third_spread_start:
                    third_spread_start = datetime.utcnow()
                if third_spread_start:
                    end_time = datetime.utcnow()
                    length = end_time - third_spread_start
                    length = length.total_seconds() / 60
                    spread_times[4] = length

                accrued_data.append((datetime.utcnow(), self.spread_with_fees))

            if start_time and self.spread_with_fees < 0.1:
                end_time = datetime.utcnow()
                length = end_time - start_time
                length = length.total_seconds()/60
                log.debug("{0}/{1}".format(self.short_exchange, self.long_exchange))
                log.debug("Max Spread: {0}% Minutes: {1}\n".format(max, length))
                spread_dict = {1:'.1% -.4%', 2:'.5% - .7%', 3: '.8%-.9%', 4: '> 1%'}

                log.debug("Spread times: {0} : {1} , {2} : {3} , {4} : {5}, {6} : {7}".format(spread_dict[1],
                                                                                              spread_times[1],
                                                                                              spread_dict[2],
                                                                                              spread_times[2],
                                                                                              spread_dict[3],
                                                                                              spread_times[3],
                                                                                              spread_dict[4],
                                                                                              spread_times[4]))

                log.debug("Values: {} \n".format(accrued_data))



                accrued_data = []
                start_time = None
                max = 0
                end_time = None
                first_spread_start = None
        	'''
