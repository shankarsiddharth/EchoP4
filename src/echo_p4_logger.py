import os
import sys
import logging
import pathlib
import threading
from logging.handlers import SocketHandler

import custom_logging as c_logging
import echo_p4_ui_logger
import echo_p4_constants as ep4c
import p4_tools_helper as p4th


class EchoP4Logger(object):
    _instance = None

    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    print('Creating the Logger object')
                    cls._instance = super(EchoP4Logger, cls).__new__(cls)
                    cls._instance.__initialize__()
        return cls._instance

    def __initialize__(self):

        self.should_log_to_ui = True

        print("Creating Logger Instance...")

        print("Getting root folder...")
        root_folder_path = p4th.get_root_folder()

        print("Checking log folder...")
        self.log_folder_path = os.path.join(root_folder_path, ep4c.LOG_FOLDER_NAME)
        self.log_folder = pathlib.Path(self.log_folder_path)
        if not self.log_folder.exists():
            print("Log folder does not exist. Creating it.")
            print("Creating log folder: " + self.log_folder_path)
            try:
                os.makedirs(self.log_folder_path)
            except OSError:
                print("Creation of the log folder %s failed" % self.log_folder_path)
                input("Press any key to exit...")
                sys.exit(1)

        print("Log Folder exists.")
        self.log_file_path = os.path.join(self.log_folder_path, ep4c.LOG_FILE_NAME)

        self.backup_log_file_path = os.path.join(self.log_folder_path, ep4c.BACKUP_LOG_FILE_NAME)

        self.log_file = pathlib.Path(self.log_file_path)
        self.backup_log_file = pathlib.Path(self.backup_log_file_path)
        maximum_log_file_size_in_MBs = 10  # 10 MB
        maximum_log_file_size_in_bytes = maximum_log_file_size_in_MBs * 1024 * 1024  # MBs to bytes

        self.logger_instance = logging.getLogger('Echo P4 Log')
        self.logger_instance.setLevel(1)  # to send all records to log

        # Attach a console handler to the logger
        console_handler = logging.StreamHandler(stream=sys.stdout)
        # create formatter
        console_formatter = logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        console_handler.setFormatter(console_formatter)
        self.logger_instance.addHandler(console_handler)

        # Attach SocketHandler - Visual Log Viewer - cutelog
        socket_handler = SocketHandler('127.0.0.1', 19996)  # default listening address
        self.logger_instance.addHandler(socket_handler)

        # Handle Log files
        log_file_write_mode = 'a'
        if self.log_file.is_file():
            # Log File Exists
            current_log_file_size = os.path.getsize(self.log_file)
            if current_log_file_size >= maximum_log_file_size_in_bytes:
                if self.backup_log_file.is_file():
                    # Backup Log file Exists
                    os.remove(self.backup_log_file_path)
                os.rename(self.log_file_path, self.backup_log_file_path)
        else:
            # Log File Does Not Exist
            log_file_write_mode = 'w'
            with open(self.log_file_path, log_file_write_mode) as log_file:
                log_file.write('')

        # Attach File Logger
        file_handler = logging.FileHandler(self.log_file_path, mode=log_file_write_mode, encoding="UTF-8")
        file_formatter = logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        file_handler.setFormatter(file_formatter)
        self.logger_instance.addHandler(file_handler)

        # Test Logs
        self.logger_instance.log(1, '======================================== Echo P4 LOGGER STARTED ========================================')
        self.logger_instance.debug('======================================== Echo P4 LOGGER STARTED ========================================')
        self.logger_instance.debug('Test Debug')
        self.logger_instance.info('Test Info')
        self.logger_instance.log(c_logging.log_level_success, 'Test Success')
        self.logger_instance.warning('Test Warning')
        self.logger_instance.error('Test Error')
        self.logger_instance.critical('Test Critical')

        self.ui_logger = None
        self.log_level = 0
        self.count = 0
        # self.flush_count = 10000

    def init_ui(self, parent=None):
        self.ui_logger = echo_p4_ui_logger.EchoP4UILogger(parent=parent)
        self.ui_logger.trace("Echo P4 UI Logger Started")
        if sys.flags.dev_mode:
            self.ui_logger.log_debug('Test Debug')
            self.ui_logger.log_info('Test Info')
            self.ui_logger.log_success('Test Success')
            self.ui_logger.log_warning('Test Warning')
            self.ui_logger.log_error('Test Error')
            self.ui_logger.log_critical('Test Critical')

    def _log(self, level, message, *args):

        if level < self.log_level:
            return

        self.count += 1

        # if self.count > self.flush_count:
        #     self.clear_log()

        self.log_message = message
        if args:
            self.log_message = message % args
            print("Compiled Message : ", self.log_message)

        if logging.NOTSET <= level < logging.DEBUG:
            self.logger_instance.log(1, message, *args)
            if self.ui_logger is not None and self.should_log_to_ui:
                self.ui_logger.trace(message, *args)

        elif level == logging.DEBUG:
            self.logger_instance.debug(message, *args)
            if self.ui_logger is not None and self.should_log_to_ui:
                self.ui_logger.debug(message, *args)

        elif level == logging.INFO:
            self.logger_instance.info(message, *args)
            if self.ui_logger is not None and self.should_log_to_ui:
                self.ui_logger.info(message, *args)

        elif level == logging.getLevelName(c_logging.log_level_success):
            self.logger_instance.log(logging.getLevelName(c_logging.log_level_success), message, *args)
            if self.ui_logger is not None and self.should_log_to_ui:
                self.ui_logger.success(message, *args)

        elif level == logging.WARNING:
            self.logger_instance.warning(message, *args)
            if self.ui_logger is not None and self.should_log_to_ui:
                self.ui_logger.warning(message, *args)

        elif level == logging.ERROR:
            self.logger_instance.error(message, *args)
            if self.ui_logger is not None and self.should_log_to_ui:
                self.ui_logger.error(message, *args)

        elif level == logging.CRITICAL:
            self.logger_instance.critical(message, *args)
            if self.ui_logger is not None:
                self.ui_logger.critical(message, *args)

        # print(message)

    def trace(self, message, *args: object):
        self._log(logging.NOTSET, message, *args)

    def debug(self, message, *args: object):
        self._log(logging.DEBUG, message, *args)

    def info(self, message, *args: object):
        self._log(logging.INFO, message, *args)

    def success(self, message, *args: object):
        self._log(logging.getLevelName(c_logging.log_level_success), message, *args)

    def warning(self, message, *args: object):
        self._log(logging.WARNING, message, *args)

    def error(self, message, *args: object):
        self._log(logging.ERROR, message, *args)

    def critical(self, message, *args: object):
        self._log(logging.CRITICAL, message, *args)

    def clear_log(self):
        pass
