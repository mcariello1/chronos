import xlwt
import datetime
import time

class ExcelLogger(object):
    def __init__(self, short_exchange_name, long_exchange_name, start_time):
        self.short_exchange_name = short_exchange_name
        self.long_exchange_name = long_exchange_name
        self.start_time = start_time
        self.time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S%f')[:-3]
        self.line_iteration = 1
        self.sheet, self.book = self.open_excel()
        self.create_heading()


    def log_excel(self, coin1, coin2, spread, growth_rate):
        self.sheet.write(self.line_iteration, 0, coin1)
        self.sheet.write(self.line_iteration, 1, coin2)
        self.sheet.write(self.line_iteration, 2, spread)
        self.sheet.write(self.line_iteration, 3, growth_rate)
        self.book.save("./results/excels/{0}/{1}{2}_{3}.xls".format(self.start_time, self.time, self.short_exchange_name, self.long_exchange_name))
        self.line_iteration += 1

    def log_excel_enter(self, short_shares, long_shares, short_coin, long_coin):

        self.sheet.write(self.line_iteration, 5, "Short Sell {0} shares @ {1}".format(short_shares, short_coin))
        self.sheet.write(self.line_iteration, 6, "Buy {0} shares @ {1}".format(long_shares,long_coin))
        self.book.save("./results/excels/{0}/{1}{2}_{3}.xls".format(self.start_time, self.time, self.short_exchange_name, self.long_exchange_name))
        self.line_iteration += 1

    def log_excel_exit(self, short_shares, long_shares, short_coin, long_coin, profit):
        self.sheet.write(self.line_iteration, 5, "Buy back {0} shares @ {1}".format(short_shares,short_coin))
        self.sheet.write(self.line_iteration, 6, "Sell {0} shares @ {1}".format(long_shares, long_coin))
        self.sheet.write(self.line_iteration, 7, "Profit is {0}".format(profit))

        self.book.save("./results/excels/{0}/{1}{2}_{3}.xls".format(self.start_time, self.time, self.short_exchange_name, self.long_exchange_name))
        self.line_iteration += 1

    def open_excel(self):

        self.book = xlwt.Workbook(encoding="utf-8")
        return self.book.add_sheet("Sheet1"), self.book


    def create_heading(self):
        self.sheet.write(0, 0, "{0}".format(self.short_exchange_name))
        self.sheet.write(0, 1, "{0}".format(self.long_exchange_name))
        self.sheet.write(0, 2, "Spread Percentage")
        self.sheet.write(0, 3, "Growth Rate")
        self.book.save("./results/excels/{0}/{1}{2}_{3}.xls".format(self.start_time, self.time, self.short_exchange_name, self.long_exchange_name))
