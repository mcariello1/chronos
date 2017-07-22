
import logging
import time
import datetime
import os




log = logging.getLogger('chronosbot')
formatter = logging.Formatter(
    '%(asctime)14s_%(msecs)03d [%(levelname).4s] [%(filename)18s:%(lineno)4s %(funcName)20s() ]  %(message)s',
    '%Y%m%d_%H%M%S')

subfold = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S%f')[:-3]


def set_log_filehandler():
    """
    Method to initialize log file handlers for per test case logging
    """
    current_dt = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S%f')[:-3]
    log = logging.getLogger('chronosbot')
    i = 0
    for item in log.handlers:
        if i == 0:
            i = i + 1
        else:
            log.removeHandler(item)
            i = i + 1
    if not os.path.exists('./results/logs/{}'.format(subfold)):
        os.makedirs('./results/logs/{}'.format(subfold))
    hdlr_server = logging.FileHandler('./results/logs/{}/{}.txt'.format(subfold, current_dt))
    hdlr_server.setFormatter(formatter)
    log.addHandler(hdlr_server)

    log.setLevel(logging.DEBUG)  # This sets what logging is sent to the file
    log.debug("#### Logging started ####")


def set_stream_handler_level(level):
    loglevel = getattr(logging, level.upper())
    log.handlers[0].setLevel(loglevel)


def pretty_print_config(list_items, depth=3):
    """
    Take a list of configuration items and make it readable for the logger.
    :param list_items: Dictinonary of configuration items.
    :return: pretty print
    """

    if (list_items is None) or (len(list_items) == 0):
        return '\n{}### None'.format('\t' * depth)

    logstatement = ''
    for key, data in list_items.items():
        if isinstance(data, dict):
            logstatement += '\n{}### {:40s}'.format('\t' * depth, key)
            logstatement += pretty_print_config(data, depth + 1)
        else:
            logstatement += '\n{}### {:40s} {}'.format('\t' * depth, key + ':', data)

    return logstatement


def log_filename():
    """ return the current log file"""
    filename = None
    for handler in log.handlers:
        if isinstance(handler, logging.FileHandler):
            filename = handler.baseFilename
    return filename


def get_recent_log_data(filename=None):
    """
    Dynamically find the information that has been printed to the current logfile
    Parse them based on standard logging start and end strings
    :param filename: used for debugging
    :return: list of strings, each representing a different test that has been run
    """

    filename = filename if filename else log_filename()
    if not filename:
        # no filehandlers active
        return None

    tests = ['']
    with open(filename, 'r') as f_obj:
        lines = f_obj.readlines()
        for line in lines:
            # add 4 spaces to the start of each line for better testrail formatting
            # remove testrail-unfriendly characters
            line = u"    {}".format(line.decode('utf-8', errors='ignore'))

            tests[-1] += line

    return tests