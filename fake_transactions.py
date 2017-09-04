


class FakeTransactions(object):
    #buys, sells, shorts, etc
    def __init__(self, name, coin):
        self.short_sell = 0
        self.buy = 0
        self.sell_price = 0
        self.buy_back_price = 0
        self.share_values = 0
        self.shares = 0
        self.beginning_amount = 0
        self.end_amount = 0
        self.name = name
        self.coin = coin

    def start_arbitrage(self):
        """
        Starts a fake abitrage transactions on given exchanges object values
        :return:
        """
        if self.short_sell:
            self.beginning_amount = self.share_values
            self.shares = float(self.share_values) / float(self.short_sell)
            print "Short sold {0} on {1} for {2} shares @ {3}".format(self.coin, self.name, self.shares, self.short_sell)
            

        if self.buy:
            self.beginning_amount = self.share_values
            self.shares = float(self.share_values) / float(self.buy)
            print "Buying {0} on {1} for {2} shares @ {3}".format(self.coin, self.name, self.shares,self.buy )


    def end_arbitrage(self):
        """
        Ends a fake arbitrage transaction on given exchanges object values
        :return:
        """
        if self.short_sell:
            self.new_shares = (float(self.share_values) / float(self.buy_back_price))
            print "Bought back litecoin on {0} for {1} shares @ {2}".format(self.name, self.shares, self.buy_back_price)
            self.end_amount = float(self.new_shares - self.shares) * float(self.buy_back_price)
            profit = self.end_amount
            self.buy_back_price = 0
            self.short_sell = 0
            self.beginning_amount = 0
            self.end_amount = 0
            return profit


        if self.buy:
            print "Sold litecoin on {0} for {1} shares @ {2}".format(self.name, self.shares, self.sell_price)
            self.end_amount = float(self.sell_price) * float(self.shares)
            profit = self.end_amount - self.beginning_amount
            self.sell_price = 0
            self.buy = 0
            self.beginning_amount = 0
            self.end_amount = 0
            return profit