
from googlevoice import Voice


class SmsLogger(object):
    def __init__(self, config):
        self.voice = Voice()
        self.voice.login('mcariello7@gmail.com', '?mcmiz123BV')
        self.config = config


    def log_sms(self, short_exchange_name, long_exchange_name, profit):
        """
        Sends an Sms when a profit is made
        :param short_exchange_name:
        :param long_exchange_name:
        :param profit:
        :return:
        """
        try:
            self.voice.send_sms(4158872108,'REAL Profit of ${0} with {1} as short and {2} as long'.format(profit, short_exchange_name,long_exchange_name))
            self.voice.send_sms(6313971667, 'REAL Profit of ${0} with {1} as short and {2} as long'.format(profit, short_exchange_name,long_exchange_name))
            self.voice.send_sms(6315173643, 'REAL Profit of ${0} with {1} as short and {2} as long'.format(profit, short_exchange_name,long_exchange_name))
        except:
            pass 

    def log_sms_informing(self, short_exchange_name, long_exchange_name):
        try:    
            self.voice.send_sms(4158872108,'Entered with {0} as high and {1} as low'.format(short_exchange_name,long_exchange_name))
            self.voice.send_sms(6313971667,'Entered with {0} as high and {1} as low'.format(short_exchange_name,long_exchange_name))
            self.voice.send_sms(6315173643,'Entered with {0} as high and {1} as low'.format(short_exchange_name,long_exchange_name)) 
        except:
            pass

    def log_sms_test(self, short_exchange_name, long_exchange_name, message):
        try:    
            self.voice.send_sms(4158872108,'With {0} as short and {1} as long: {2} '.format(short_exchange_name,long_exchange_name, message))
        except:
            pass
