"""
This module handles all Global values
"""

# pylint: disable=E0401
from tornado.httpclient import AsyncHTTPClient

UPLOAD_DATA_COUNT = 0
DICT_DATA = None
ID_COUNTER = 0
async_http_client = AsyncHTTPClient()
