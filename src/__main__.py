import sys

from app_utility import AppUtility
from app_globals import log
from app_error import AppError
from app_exit import AppExit
from app_message import AppMessage
from application_initial_setup import ApplicationInitialSetup

if __name__ == "__main__":
    try:
        ApplicationInitialSetup()
        log.info("Starting the application...")
        AppUtility()
    except AppExit as e:
        log.info("Application Exited by User.")
        if sys.flags.dev_mode:
            raise e
        sys.exit(0)
    except AppMessage as e:
        if sys.flags.dev_mode:
            raise e
        sys.exit(0)
    except AppError as e:
        log.exception(e)
        if sys.flags.dev_mode:
            raise e
        sys.exit(0)
    except BaseException as e:
        log.exception(e)
        if sys.flags.dev_mode:
            raise e
        sys.exit(0)
