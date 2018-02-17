


class SpreadTracking(object):
    def __init__(self, max_array, short_exchange, long_exchange, coin):
        self.max_array_size = max_array
        self.spread = 0
        self.spread_with_fees = 0
        self.trailing_array = []
        self.growth_rate = 0
        self.short_exchange = short_exchange
        self.long_exchange = long_exchange
        self.short_coin = 0
        self.long_coin = 0
        self.coin_type = coin

    def get_growth_rate(self):
        """
        Given an array of trailing spreads determine what the growth rate of the spreads are
        :param trailing_array: An array of spread that is filled by the arbitrage thread
        :return: the growth rate of the set of given values
        """
        if self.trailing_array <= 1:
            return 0
        else:
            self.growth_rate = (self.trailing_array[len(self.trailing_array) - 1] / self.trailing_array[0]) ** (1 / float(len(self.trailing_array))) - 1

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




