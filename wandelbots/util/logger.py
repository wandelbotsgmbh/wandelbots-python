import logging

# TODO: Change this whenever the package name changes
_ROOT_LOGGER_NAME = "wandelbots"


def _get_logger(name: str):
    """
    Get a logger instance with the given name.

    Args:
        name (str): The name of the logger.
    """
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    return logger


def setup_logging(level=logging.INFO, format_str=None):
    """
    Sets up logging for the nova_client library.

    Args:
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
        format_str (str, optional): Logging format string.
    """
    if format_str is None:
        format_str = "[%(asctime)s] [nova_client] %(levelname)s: %(name)s:%(lineno)d %(message)s"

    handler = logging.StreamHandler()
    formatter = logging.Formatter(format_str, "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    logger = logging.getLogger(_ROOT_LOGGER_NAME)
    logger.setLevel(level)
    logger.addHandler(handler)
