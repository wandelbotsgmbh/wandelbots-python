import logging

# Config params
TIMEOUT = 30

# Logging
httpx_logger = logging.getLogger("httpx")  # Suppress httpx info logs
httpx_logger.setLevel(logging.WARNING)  # Set the logging level to WARNING to suppress INFO logs
requests_logger = logging.getLogger("requests")  # Suppress requests info logs
requests_logger.setLevel(logging.WARNING)  # Set the logging level to WARNING to suppress INFO logs
