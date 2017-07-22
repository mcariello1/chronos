

import os
from xml.dom import minidom

def parse_config(config_dir='configs'):
    """
    Parses all necessary configs
    :param config_dir:
    :return:
    """
    exchange_dict = {}
    config_list = {}
    config_file = 'chronos.xml'
    doc = minidom.parse(os.path.join(config_dir, config_file))
    root = doc.getElementsByTagName("chronosconfig")
    exchange = root[0].getElementsByTagName("exchange")

    for config in exchange:
        every_config_value = config.getElementsByTagName("global")
        config_name = config.getAttribute("name")
        for config_value in every_config_value:
            name = config_value.getAttribute("name")
            config_list[name] = config_value.getAttribute("value")
        exchange_dict[config_name] = config_list
        config_list = {}

    return exchange_dict