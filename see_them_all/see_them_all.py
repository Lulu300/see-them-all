from event_bus import EventBus
from logging.handlers import RotatingFileHandler
from util.constants import EB_NEW_SEEN_EP, bus
from logger import Logger
import logging
import time
import argparse
import json
import importlib
import atexit


class SeeThemAll(object):

    def __init__(self, config):
        self.config = config

    def start(self):
        self.setup_outputs()
        self.setup_inputs()

    def setup_outputs(self):
        enabled_outputs = self.reduce_entries(self.config.get('outputs').items())
        for output_name, output_config in enabled_outputs:
            type_ = output_config.get('type')
            module_name = '.'.join(type_.split('.')[0:-1])
            class_name = type_.split('.')[-1]
            try:
                module = __import__(module_name, fromlist=[class_name])
                klass = getattr(module, class_name)
                output_ = klass(output_name, output_config, self.config.get('cache_folder'))
                try:
                    for input_name in output_config.get('inputs'):
                        bus.add_event(output_.mark_as_watched, '{0}:{1}'.format(EB_NEW_SEEN_EP, input_name))
                    atexit.register(output_.write_cache_to_file)
                except Exception as e:
                    logging.error(e)
            except Exception as e:
                logging.warning(e)

    def setup_inputs(self):
        enabled_inputs = self.reduce_entries(self.config.get('inputs').items())
        for input_name, input_config in enabled_inputs:
            type_ = input_config.get('type')
            module_name = '.'.join(type_.split('.')[0:-1])
            class_name = type_.split('.')[-1]
            try:
                module = __import__(module_name, fromlist=[class_name])
                klass = getattr(module, class_name)
                input_ = klass(input_name, input_config, self.config.get('cache_folder'))
                try:
                    input_.recently_watched()
                except Exception as e:
                    logging.error(e)
            except Exception as e:
                logging.warning(e)

    def reduce_entries(self, entries):
        for entry_name, entry in entries:
            if entry.get('enabled'):
                yield entry_name, entry


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='See Them All!')
    parser.add_argument('--config', help="Path to config file", type=str, default='/etc/see_them_all.json')
    args = parser.parse_args()

    # TODO: Check config file with avro schema
    with open(args.config, 'r') as f:
        config = json.load(f)

    Logger.getInstance().setup_logger(config.get('log'))

    see_them_all = SeeThemAll(config)
    see_them_all.start()
