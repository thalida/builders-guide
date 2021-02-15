import log
import os
import logging

os.environ["TZ"] = "UTC"
logger = logging.getLogger(__name__)

import cProfile, pstats
from line_profiler import LineProfiler
import sys
import time
import functools

from flask import make_response, json
import gzip

def profile(func):
    @functools.wraps(func)
    def wrapper_profile(*args, **kwargs):
        ts = time.time()
        profiler = cProfile.Profile()
        profiler.enable()

        func_res = func(*args, **kwargs)

        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        # stats.print_stats()
        stats.dump_stats(f'./.profiler/{func.__name__}__{ts}')

        return func_res

    return wrapper_profile


def line_profile(func):
    @functools.wraps(func)
    def wrapper_line_profile(*args, **kwargs):
        ts = time.time()
        profiler = LineProfiler()
        profiled_func = profiler(func)

        try:
            func_res = profiled_func(*args, **kwargs)
        finally:
            filename = f'./.profiler/{func.__name__}__lines.txt'
            original_stdout = sys.stdout
            with open(filename, 'a') as f:
                sys.stdout = f # Change the standard output to the file we created.
                profiler.print_stats()
                print('\n\n')
                print('=================END RUN ================')
                print('\n\n')
                sys.stdout = original_stdout # Reset the standard output to its original value

        return func_res

    return wrapper_line_profile


def compress(func):
    @functools.wraps(func)
    def wrapper_compress(*args, **kwargs):
        res_data = func(*args, **kwargs)

        content = gzip.compress(json.dumps(res_data).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response

    return wrapper_compress
