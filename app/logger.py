import logging
import time

class Logger:
    formatter = logging.Formatter('%(asctime)s %(name)-11s [%(levelname)s] %(message)s')

    file_handler = logging.FileHandler(f'../log/{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}.log')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(Logger.file_handler)
        self.logger.addHandler(Logger.console_handler)

        self.logger.info(f'Logger {name} created')

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)