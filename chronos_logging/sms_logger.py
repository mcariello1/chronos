
from googlevoice import Voice


class SmsLogger(object):
    def __init__(self, config):
        self.voice = Voice()
        self.voice.login('mcariello7@gmail.com', '?mcmiz123VZ')
        self.config = config


    def log_sms(self, short_exchange_name, long_exchange_name, profit):
        """
        Sends an Sms when a profit is made
        :param short_exchange_name:
        :param long_exchange_name:
        :param profit:
        :return:
        """
        self.voice.send_sms(4158872108,'REAL Profit of ${0} with {1} as short and {2} as long'.format(profit, short_exchange_name,long_exchange_name))
        self.voice.send_sms(6313971667, 'REAL Profit of ${0} with {1} as short and {2} as long'.format(profit, short_exchange_name,long_exchange_name))
        self.voice.send_sms(6315173643, 'REAL Profit of ${0} with {1} as short and {2} as long'.format(profit, short_exchange_name,long_exchange_name))


    def log_sms_informing(self, short_exchange_name, long_exchange_name):
            self.voice.send_sms(4158872108,'Entered with {0} as high and {1} as low'.format(short_exchange_name,long_exchange_name))
            self.voice.send_sms(6313971667,'Entered with {0} as high and {1} as low'.format(short_exchange_name,long_exchange_name))
            self.voice.send_sms(6315173643,'Entered with {0} as high and {1} as low'.format(short_exchange_name,long_exchange_name))