"""
This is a module that handles all the configuration used for OpenSearch testing
"""

import logging
import os

from tornado.options import define
from tornado.options import parse_config_file, options

define(
    "action",
    type=str,
    default="all",
    help="Specify the action to be performed. The available options are \
[generate_data, query_all, custom_query, \
period_breakdown_query, delete_index, all]",
)
define("json_path", type=str, default=None, help="Query JSON file path")
define(
    "opensearch_url",
    type=str,
    default="http://localhost:9200",
    help="URL of your Opensearch node",
)
define(
    "index_name",
    type=str,
    default="test",
    help="Name of the index to store your messages",
)
define("index_type", type=str, default="test_type", help="index Type")
define(
    "batch_size",
    type=int,
    default=1000,
    help="opensearch bulk index batch size",
)
define(
    "number_of_shards",
    type=int,
    default=1,
    help="Number of shards for OS index",
)
define(
    "http_upload_timeout",
    type=int,
    default=10,
    help="Timeout in seconds when uploading data",
)
define("count", type=int, default=100000, help="Number of docs to generate")
define(
    "number_of_replicas",
    type=int,
    default=1,
    help="Number of replicas for OpenSearch index",
)
define(
    "force_init_index",
    type=bool,
    default=False,
    help="Force deleting and re-initializing the opensearch index",
)
define(
    "set_refresh",
    type=bool,
    default=False,
    help="Set refresh rate to -1 before starting the upload",
)
define(
    "out_file",
    type=bool,
    default=False,
    help="If set,write test data to out_file as well.",
)
define(
    "id_type",
    type=str,
    default=None,
    help="Type of 'id' to use for the docs, int and uuid4",
)
define(
    "dict_file", type=str, default=None, help="Name of dictionary file to use"
)
define(
    "data_file",
    type=str,
    default=None,
    help="Name of the documents file to use",
)
define("username", type=str, default=None, help="Username for opensearch")
define("password", type=str, default=None, help="Password for opensearch")
define(
    "client_cert",
    type=str,
    default=None,
    help="filepath of CA certificates in PEM format",
)
define(
    "client_key",
    type=str,
    default=None,
    help="filepath of for client SSL key",
)
define(
    "validate_cert",
    type=bool,
    default=True,
    help="SSL validate_cert for requests. \
       Use false for self-signed certificates.",
)
define(
    "random_seed", type=int, default=None, help="Random Seed number for Faker"
)
define(
    "start_time",
    type=str,
    default=None,
    help="'%Y-%m-%d %H:%M:%S' Shape Start Time",
)
define(
    "finish_time",
    type=str,
    default=None,
    help="'%Y-%m-%d %H:%M:%S' Shape Finish Time)",
)
define(
    "format",
    type=str,
    default="name:str,age:int,last_updated:ts",
    help="message format",
)


def load_config(config_file_path):
    """
    Parses and loads the config file at the given path.
    """
    if not os.path.isfile(config_file_path):
        logging.info(
            "%s does not exist. only parse command line", config_file_path
        )
        options.parse_command_line()
    else:
        parse_config_file(config_file_path)
