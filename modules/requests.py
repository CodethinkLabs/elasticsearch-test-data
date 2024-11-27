"""
This module handles functions related to HTTP requests
"""

# pylint: disable=E0401
import os
import json
import logging

import tornado
from tornado.options import options
from tornado.httpclient import HTTPRequest, HTTPClient, HTTPError
from tornado.httputil import HTTPHeaders

from .generate_data import (
    set_finish_time,
    set_start_time,
)
from . import shared


def request_https_parameters(
    url, request_method, body=None, request_timeout=240
):
    """
    Generate HTTP Request Parameters
    """
    headers = HTTPHeaders({"content-type": "application/json"})

    request_parameters = {
        "url": url,
        "headers": headers,
        "method": request_method,
        "request_timeout": request_timeout,
        "auth_username": options.username,
        "auth_password": options.password,
        "validate_cert": options.validate_cert,
    }

    if options.client_key is not None:
        request_parameters.update({"client_key": options.client_key})

    if options.client_cert is not None:
        request_parameters.update({"client_cert": options.client_cert})

    if body is not None:
        request_parameters.update({"body": body})

    return request_parameters


def delete_index(idx_name):
    """
    This Function Delete Index
    """
    try:
        url = f"{options.opensearch_url}/{idx_name}"
        request_parameters = request_https_parameters(url, "DELETE")
        request = HTTPRequest(**request_parameters)
        response = HTTPClient().fetch(request)
        logging.info("Deleting index '%s' done %s", idx_name, response.body)
    except HTTPError as e:
        logging.info("Error while Deleting index %s", e)


def create_index(idx_name):
    """
    This Function Create Index
    """
    schema = {
        "settings": {
            "index": {
                "number_of_shards": options.number_of_shards,
                "number_of_replicas": options.number_of_replicas,
            }
        }
    }

    body = json.dumps(schema)
    url = f"{options.opensearch_url}/{idx_name}"
    request_parameters = request_https_parameters(url, "PUT", body)
    try:
        logging.info("Trying to create index %s", url)
        request = HTTPRequest(**request_parameters)
        response = HTTPClient().fetch(request)
        result = json.loads(response.body.decode("utf-8"))
        logging.info("Creating index %s done   %s", idx_name, result)
    except HTTPError:
        logging.info("Looks like the index exists already")


@tornado.gen.coroutine
def upload_batch(upload_data_txt):
    # pylint: disable=W0718
    """
    This Function Upload Batches
    """
    url = f"{options.opensearch_url}/_bulk"
    request_parameters = request_https_parameters(
        url, "POST", upload_data_txt, options.http_upload_timeout
    )
    try:
        request = HTTPRequest(**request_parameters)
        response = HTTPClient().fetch(request)

        result = json.loads(response.body.decode("utf-8"))
        res_txt = "OK" if not result["errors"] else "FAILED"
        took = int(result["took"])
        logging.info(
            "Upload: %s - upload took: %5dms, total docs uploaded: %7d",
            res_txt,
            took,
            shared.UPLOAD_DATA_COUNT,
        )

    except HTTPError as e:
        logging.error("upload failed, HTTP error: %s", e)

    except Exception as e:
        logging.error("Unexpected Error Occured: %s", e)


def set_index_refresh(val):
    # pylint: disable=W0718
    """
    Refresh Index of Opensearch DB
    """
    body = json.dumps({"index": {"refresh_interval": val}})
    url = f"{options.opensearch_url}/{options.index_name}/_settings"
    request_parameters = request_https_parameters(url, "PUT", body)
    try:
        request = HTTPRequest(**request_parameters)
        HTTPClient().fetch(request)
        logging.info("Set index refresh to %s", val)
    except HTTPError as e:
        logging.exception("HTTP Error while index refresh %s", e)


def initial_search():
    """
    Performs the initial search and returns the scroll ID and total hits
    """
    url = f"{options.opensearch_url}/{options.index_name}\
/_search?scroll=1m&request_cache=false"

    start_time = set_start_time()
    finish_time = set_finish_time()

    query = {
        "size": 10000,
        "query": {
            "range": {
                "@timestamp": {
                    "gte": start_time,
                    "lte": finish_time,
                }
            }
        },
        "track_total_hits": True,
    }

    body = json.dumps(query)
    request_parameters = request_https_parameters(url, "POST", body)

    try:
        request = HTTPRequest(**request_parameters)
        response = HTTPClient().fetch(request)
        result = json.loads(response.body.decode("utf-8"))
        total_hits = int(result["hits"]["total"]["value"])
        scroll_id = result["_scroll_id"]
        took = result["took"]

    except HTTPError as e:
        logging.error("Initial search failed, HTTP error: %s", e)

    return scroll_id, total_hits, took


def scroll_search(scroll_id):
    """
    Performs a scroll search using the provided scroll ID
    """
    url = f"{options.opensearch_url}/_search/scroll"

    body = json.dumps({"scroll": "1m", "scroll_id": scroll_id})
    request_parameters = request_https_parameters(url, "POST", body)

    try:
        request = HTTPRequest(**request_parameters)
        response = HTTPClient().fetch(request)
        result = json.loads(response.body.decode("utf-8"))
        scroll_id = result["_scroll_id"]
        took = result["took"]

    except HTTPError as e:
        logging.error("Scroll search failed, HTTP error: %s", e.code)

    return scroll_id, took


def clear_scroll(scroll_id):
    """
    Clears the scroll context
    """
    url = f"{options.opensearch_url}/_search/scroll/\
{scroll_id}"

    request_parameters = request_https_parameters(url, "DELETE")
    request = HTTPRequest(**request_parameters)

    try:
        HTTPClient().fetch(request)
        logging.info("Scroll context cleared successfully")
    except HTTPError as e:
        logging.error("Failed to clear scroll context, HTTP error: %s", e.code)


def query_all_opensearch():
    """
    Queries the OpenSearch index for all data
    within the specified time range using scroll API
    """
    scroll_id, total_hits, total_time = initial_search()

    total_pages = (total_hits + 9999) // 10000
    logging.info("Total hits: %d, Total pages: %d", total_hits, total_pages)

    for page_number in range(total_pages):
        scroll_id, scroll_time = scroll_search(scroll_id)
        total_time += scroll_time
        logging.info("Retrieved page %d of %d", page_number + 1, total_pages)

    clear_scroll(scroll_id)

    logging.info("Total Querying time taken: %.2fms", total_time)


def custom_query_opensearch(json_path):
    """
    Queries the OpenSearch with custom query json file
    """
    url = f"{options.opensearch_url}/{options.index_name}\
/_search?request_cache=false"

    if os.path.isfile(json_path):
        logging.error("Cannot find JSON file")
        return None

    with open(json_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    body = json.dumps(json_data)
    request_parameters = request_https_parameters(url, "POST", body)

    try:
        request = HTTPRequest(**request_parameters)
        response = HTTPClient().fetch(request)
        result = json.loads(response.body.decode("utf-8"))
        took = result["took"]
        logging.info("Total Querying time taken: %sms", took)

    except HTTPError as e:
        logging.error("Initial search failed, HTTP error: %s", e)
