import os
import sys
import logging


def initialize_logger():
    if not os.path.isdir('reports'):
        os.mkdir('reports')

    logger = logging.getLogger(__name__)
    logger.setLevel("DEBUG")

    # Handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = logging.FileHandler(filename=f'reports/test_log.log', mode='w')
    c_handler.setLevel("DEBUG")
    f_handler.setLevel("DEBUG")

    # Formatting
    c_format = logging.Formatter('{asctime}.{msecs:03.0f} | {module:^20} | {funcName:^30} | {levelname:^10} | {message}',
                                 datefmt='%Y-%m-%d %H:%M:%S',
                                 style='{')
    f_format = logging.Formatter('{asctime}.{msecs:03.0f} | {module:^20} | {funcName:^30} | {levelname:^10} | {message}',
                                 datefmt='%Y-%m-%d %H:%M:%S',
                                 style='{')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


logger = initialize_logger()
