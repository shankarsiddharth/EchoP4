# ========================== START Log Constants ===================================
import logging
log_level_success = logging.INFO + 5
log_level_exception = logging.CRITICAL + 10
logging.addLevelName(log_level_success, "SUCCESS")
logging.addLevelName(log_level_exception, "EXCEPTION")
# ========================== END Log Constants ===================================

# ****************************************************************************************************************************************************************
