import os
import sys
import traceback
import logging
import logstash_async.handler
import logstash_async.formatter


if os.environ.get('BG_HOST') is not None:
    warning_only_libs = []

    for lib in warning_only_libs:
        logging.getLogger(lib).setLevel(logging.WARNING)


    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    logstash_handler = logstash_async.handler.AsynchronousLogstashHandler(
        os.environ['BG_HOST'],
        5959,
        database_path=None
    )
    logstash_formatter = logstash_async.formatter.FlaskLogstashFormatter()
    logstash_handler.setFormatter(logstash_formatter)
    root_logger.addHandler(logstash_handler)

    def handle_excepthook(exctype, value, tb):
        uncaught_logger = logging.getLogger('uncaught')
        message = ''.join(traceback.format_exception(exctype, value, tb))
        uncaught_logger.critical(message)

    sys.excepthook = handle_excepthook
