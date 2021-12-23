import os
import logging

os.environ["TZ"] = "UTC"
logger = logging.getLogger(__name__)

import functools
from flask import make_response, json

def json_response(func):
    @functools.wraps(func)
    def wrapper_compress(*args, **kwargs):
        res_data = func(*args, **kwargs)

        content = json.dumps(res_data)
        response = make_response(content)
        response.mimetype = 'application/json'
        return response

    return wrapper_compress
