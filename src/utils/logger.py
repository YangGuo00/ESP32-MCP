import logging
import sys
from typing import Optional


_loggers = {}


def get_logger(name: str = __name__) -> logging.Logger:
    """获取或创建日志记录器"""
    if name not in _loggers:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)

            logger.addHandler(handler)

        _loggers[name] = logger

    return _loggers[name]


def set_log_level(level: str):
    """设置全局日志级别"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    for logger in _loggers.values():
        logger.setLevel(log_level)
        for handler in logger.handlers:
            handler.setLevel(log_level)
