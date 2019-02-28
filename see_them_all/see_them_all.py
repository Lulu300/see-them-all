from DaemonLite import DaemonLite
from event_bus import EventBus
from logging.handlers import RotatingFileHandler
from util.constants import bus
from logger import Logger
import logging
import time
import argparse
import json
import importlib
import threading


class SeeThemAll(DaemonLite):

    def __init__(self, config):
        DaemonLite.__init__(self, pidFile=config.get('pid_file'))
        self.config = config

    def run(self):
        self.setup_outputs()
        self.setup_inputs()

    def setup_outputs(self):
        for output_name, output_config in self.config.get('outputs').items():
            if output_config.get('enabled'):
                type_ = output_config.get('type')
                module_name = '.'.join(type_.split('.')[0:-1])
                class_name = type_.split('.')[-1]
                try:
                    module = __import__(module_name, fromlist=[class_name])
                    klass = getattr(module, class_name)
                    output_ = klass(output_config)
                    for input_name in output_config.get('inputs'):
                        bus.add_event(output_.mark_as_watched, 'new:seen:episodes:{0}'.format(input_name))
                except Exception as e:
                    print(e)
                    logging.warning('No output with path {0} found.'.format(type_))

    def setup_inputs(self):
        for input_name, input_config in self.config.get('inputs').items():
            if input_config.get('enabled'):
                type_ = input_config.get('type')
                module_name = '.'.join(type_.split('.')[0:-1])
                class_name = type_.split('.')[-1]
                try:
                    module = __import__(module_name, fromlist=[class_name])
                    klass = getattr(module, class_name)
                    input_ = klass(input_name, input_config)
                    self.start_input(input_)
                except Exception as e:
                    print(e)
                    logging.warning('No input with path {0} found.'.format(type_))

    def start_input(self, input_):
        input_.recently_watched()
        threading.Timer(input_.config.get('interval'), self.start_input, args=[input_]).start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='See Them All!')
    parser.add_argument('--config', help="Path to config file", type=str, default='/etc/see_them_all.json')
    parser.add_argument('--fg', help="Run the program in the foreground", action='store_true')
    args = parser.parse_args()

    # TODO: Check config file with avro schema
    with open(args.config, 'r') as f:
        config = json.load(f)

    Logger.getInstance().setup_logger(config.get('log'))

    staff = SeeThemAll(config)
    if args.fg:
        staff.run()
    else:
        staff.start()
