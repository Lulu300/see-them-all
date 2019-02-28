from logging.handlers import RotatingFileHandler
import logging


class Logger:
    __instance = None

    @staticmethod
    def getInstance():
        if Logger.__instance is None:
            Logger()
        return Logger.__instance

    def __init__(self):
        if Logger.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Logger.__instance = self

    @staticmethod
    def setup_logger(config):
        # Create logger
        logger = logging.getLogger()
        log_level = logging.getLevelName(config['level'])
        logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s :: %(module)s :: %(levelname)s :: %(message)s')

        # Create a file handler for the log
        file_handler = RotatingFileHandler(
            filename=config['path'], mode='a', maxBytes=config['max_size'],
            backupCount=config['backup_count']
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Create a stream handler to display log on console
        if config['show_on_console']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(log_level)
            logger.addHandler(stream_handler)
