import os
import sys
import logging
import pathlib
from logging.handlers import SocketHandler

import echo_p4_ui_logger
import echo_p4_constants


class EchoP4Logger:

    def __init__(self, log_folder_path=None, log_file_path=None, backup_log_file_path=None, print_test_log=False):

        if log_folder_path is None or log_file_path is None or backup_log_file_path is None:
            return

        self.log_folder_path = log_folder_path
        self.log_file_path = log_file_path
        self.backup_log_file_path = backup_log_file_path

        log_file = pathlib.Path(self.log_file_path)
        backup_log_file = pathlib.Path(self.backup_log_file_path)
        maximum_log_file_size_in_MBs = 10  # 10 MB
        maximum_log_file_size_in_bytes = maximum_log_file_size_in_MBs * 1024 * 1024  # MBs to bytes

        echo_p4_logger = logging.getLogger('Echo P4 Log')
        echo_p4_logger.setLevel(1)  # to send all records to log

        # Attach a console handler to the logger
        console_handler = logging.StreamHandler(stream=sys.stdout)
        # create formatter
        console_formatter = logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        console_handler.setFormatter(console_formatter)
        echo_p4_logger.addHandler(console_handler)

        # Attach SocketHandler - Visual Log Viewer - cutelog
        socket_handler = SocketHandler('127.0.0.1', 19996)  # default listening address
        echo_p4_logger.addHandler(socket_handler)

        # Handle Log files
        log_file_write_mode = 'a'
        if log_file.is_file():
            # Log File Exists
            current_log_file_size = os.path.getsize(log_file)
            if current_log_file_size >= maximum_log_file_size_in_bytes:
                if backup_log_file.is_file():
                    # Backup Log file Exists
                    os.remove(backup_log_file_path)
                    pass
                os.rename(log_file_path, backup_log_file_path)

        # Attach File Logger
        file_handler = logging.FileHandler(log_file_path, mode=log_file_write_mode)
        file_formatter = logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        file_handler.setFormatter(file_formatter)
        echo_p4_logger.addHandler(file_handler)

        if print_test_log:
            # Test Logs
            echo_p4_logger.log(1, '======================================== Echo P4 LOGGER STARTED ========================================')
            echo_p4_logger.debug('======================================== Echo P4 LOGGER STARTED ========================================')
            echo_p4_logger.debug('Test Debug')
            echo_p4_logger.info('Test Info')
            echo_p4_logger.warning('Test Warning')
            echo_p4_logger.error('Test Error')
            echo_p4_logger.critical('Test Critical')

        self.ui_logger = None
        self.echo_p4_logger = echo_p4_logger
        self.log_level = 0
        self.count = 0
        # self.flush_count = 10000

    def init_ui(self, parent=None, is_debug=False):
        self.ui_logger = echo_p4_ui_logger.EchoP4UILogger(parent=parent)
        self.ui_logger.trace("Echo P4 UI Logger Started")
        if is_debug:
            self.ui_logger.log_debug('Test Debug')
            self.ui_logger.log_info('Test Info')
            self.ui_logger.log_warning('Test Warning')
            self.ui_logger.log_error('Test Error')
            self.ui_logger.log_critical('Test Critical')

    def _log(self, message, level, should_log_to_ui):

        if level < self.log_level:
            return

        self.count += 1

        # if self.count > self.flush_count:
        #     self.clear_log()

        if logging.NOTSET <= level < logging.DEBUG:
            self.echo_p4_logger.log(level=1, msg=message)
            if self.ui_logger is not None and should_log_to_ui:
                self.ui_logger.trace(message)

        elif level == logging.DEBUG:
            self.echo_p4_logger.debug(msg=message)
            if self.ui_logger is not None and should_log_to_ui:
                self.ui_logger.log_debug(message)

        elif level == logging.INFO:
            self.echo_p4_logger.info(msg=message)
            if self.ui_logger is not None and should_log_to_ui:
                self.ui_logger.log_info(message)

        elif level == logging.WARNING:
            self.echo_p4_logger.warning(msg=message)
            if self.ui_logger is not None and should_log_to_ui:
                self.ui_logger.log_warning(message)

        elif level == logging.ERROR:
            self.echo_p4_logger.error(msg=message)
            if self.ui_logger is not None and should_log_to_ui:
                self.ui_logger.log_error(message)

        elif level == logging.CRITICAL:
            self.echo_p4_logger.critical(msg=message)
            if self.ui_logger is not None:
                self.ui_logger.log_critical(message)

        # print(message)

    def trace(self, message, should_log_to_ui=True):
        self._log(message, logging.NOTSET, should_log_to_ui)

    def debug(self, message, should_log_to_ui=True):
        self._log(message, logging.DEBUG, should_log_to_ui)

    def info(self, message, should_log_to_ui=True):
        self._log(message, logging.INFO, should_log_to_ui)

    def warning(self, message, should_log_to_ui=True):
        self._log(message, logging.WARNING, should_log_to_ui)

    def error(self, message, should_log_to_ui=True):
        self._log(message, logging.ERROR, should_log_to_ui)

    def critical(self, message, should_log_to_ui=True):
        self._log(message, logging.CRITICAL, should_log_to_ui)

    def clear_log(self):
        pass
