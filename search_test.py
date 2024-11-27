"""
Entry Point
"""

# pylint: disable=E0401
import time
import logging
import nest_asyncio
import tornado
from tornado.options import options
from modules.config import load_config
from modules.upload_data import generate_test_data
from modules.requests import (
    custom_query_search,
    query_all,
    delete_index,
)


def check_options():
    """
    Raise Error if there is nothing to do
    """
    active_options = [
        "generate_data",
        "query_all",
        "delete_index",
        "custom_query",
        "all"
    ]

    if options.action not in active_options:
        logging.error("Nothing to do, check the options")


def main():
    """
    Main fuction for search_test
    """
    nest_asyncio.apply()
    load_config("server.conf")
    check_options()

    if options.action in ("generate_data", "all"):
        logging.info("***Start Data Generate Test***")
        time.sleep(3)
        tornado.ioloop.IOLoop.instance().run_sync(generate_test_data)

    if options.action in ("query_all", "all"):
        logging.info("***Start Query All Test***")
        time.sleep(3)
        tornado.ioloop.IOLoop.instance().run_sync(query_all)

    if options.action == "custom_query":
        logging.info("***Start Query test by using '%s'***", options.json_path)
        time.sleep(3)
        custom_query_search(options.json_path)

    if options.action in ("delete_index", "all"):
        logging.info("***Start Delete Index***")
        time.sleep(3)
        delete_index(options.index_name)


if __name__ == "__main__":
    main()
