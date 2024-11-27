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
    custom_query_opensearch,
    query_all_opensearch,
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
    Main fuction for opensearch_test_data_generator
    """
    nest_asyncio.apply()
    load_config("server.conf")
    check_options()

    if options.action in ("generate_data", "all"):
        logging.info("***Start Data Generate Test***")
        time.sleep(1)
        tornado.ioloop.IOLoop.instance().run_sync(generate_test_data)

    if options.action in ("query_all", "all"):
        logging.info("***Start Query All Test***")
        time.sleep(1)
        tornado.ioloop.IOLoop.instance().run_sync(query_all_opensearch)

    if options.action == "custom_query":
        logging.info("***Start Query test by using '%s'***", options.json_path)
        time.sleep(1)
        custom_query_opensearch(options.json_path)

    if options.action in ("delete_index", "all"):
        logging.info("***Start Delete Index***")
        time.sleep(1)
        delete_index(options.index_name)


if __name__ == "__main__":
    main()
