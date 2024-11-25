# import logging
#
# class CustomFormatter(logging.Formatter):
#     FORMATS = {
#         logging.DEBUG: "\33[35m[%(asctime)s] [%(levelname)s] %(message)s\33[0m",  # Magenta
#         logging.INFO: "\33[36m[%(asctime)s] [%(levelname)s] %(message)s\33[0m",   # Cyan
#         logging.WARNING: "\33[33m[%(asctime)s] [%(levelname)s] %(message)s\33[0m",  # Yellow
#         logging.ERROR: "\33[31m[%(asctime)s] [%(levelname)s] %(message)s\33[0m",    # Red
#         logging.CRITICAL: "\33[41m[%(asctime)s] [%(levelname)s] %(message)s\33[0m"  # Red background
#     }
#
#     def format(self, record):
#         log_fmt = self.FORMATS.get(record.levelno)
#         formatter = logging.Formatter(log_fmt)
#         return formatter.format(record)
# logger = logging.getLogger(__name__)
# handler = logging.StreamHandler()
# handler.setFormatter(CustomFormatter())
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)


import logging

# Define custom log levels
TRACE = 5
SUCCESS = 25
NOTICE = 35

logging.addLevelName(TRACE, "TRACE")
logging.addLevelName(SUCCESS, "SUCCESS")
logging.addLevelName(NOTICE, "NOTICE")

class CustomFormatter(logging.Formatter):
    FORMATS = {
        TRACE: "\33[34m[%(asctime)s] [%(levelname)s] %(message)s\33[0m",       # Blue
        logging.DEBUG: "\33[35m[%(asctime)s] [%(levelname)s] %(message)s\33[0m",  # Magenta
        logging.INFO: "\33[36m%(asctime)s ( %(levelname)s ) -->  %(message)s\33[0m",   # Cyan
        SUCCESS: "\33[32m%(asctime)s - ( %(levelname)s ) -->  %(message)s\33[0m",     # Green
        logging.WARNING: "\33[33m[%(asctime)s] [%(levelname)s] %(message)s\33[0m",  # Yellow
        NOTICE: "\33[38;5;208m[%(asctime)s] [%(levelname)s] %(message)s\33[0m", # Orange
        logging.ERROR: "\33[31m[%(asctime)s] [%(levelname)s] %(message)s\33[0m",    # Red
        logging.CRITICAL: "\33[41m[%(asctime)s] [%(levelname)s] %(message)s\33[0m"  # Red background
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        if log_fmt:
            formatter = logging.Formatter(log_fmt)
        else:
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        return formatter.format(record)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Add methods for custom levels
def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kwargs)

def notice(self, message, *args, **kwargs):
    if self.isEnabledFor(NOTICE):
        self._log(NOTICE, message, args, **kwargs)

logging.Logger.trace = trace
logging.Logger.success = success
logging.Logger.notice = notice

# Example usage
# logger.trace("This is a trace message")
# logger.debug("This is a debug message")
# logger.info("This is an info message")
# logger.success("This is a success message")
# logger.warning("This is a warning message")
# logger.notice("This is a notice message")
# logger.error("This is an error message")
# logger.critical("This is a critical message")