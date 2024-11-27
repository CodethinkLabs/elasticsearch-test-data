"""
This module includes functions used to upload
generated fake data to an OpenSearch database.
"""

# pylint: disable=E0401
import json
import logging
import sys
import time

import tornado
from tornado.options import options

from .generate_data import (
    csv_file_to_json,
    generate_random_doc,
)
from .requests import (
    delete_index,
    create_index,
    set_index_refresh,
    upload_batch,
)
from . import shared


@tornado.gen.coroutine
def generate_test_data():
    # pylint: disable=R0912,R0915, R1732
    """
    Upload Test Data
    """

    if options.force_init_index:
        delete_index(options.index_name)

    create_index(options.index_name)

    if options.set_refresh:
        set_index_refresh("-1")

    if options.out_file:
        out_file = open(options.out_file, "w", encoding="utf-8")
    else:
        out_file = None

    if options.dict_file:
        with open(options.dict_file, "r", encoding="utf-8") as f:
            shared.DICT_DATA = f.readlines()
        logging.info(
            "Loaded %d words from the %s",
            len(shared.DICT_DATA),
            options.dict_file,
        )

    fmt = options.format.split(",")
    if not fmt:
        logging.error("invalid format")
        sys.exit(1)

    ts_start = int(time.time())
    upload_data_txt = ""

    if options.data_file:
        json_array = ""
        if options.data_file.endswith(".csv"):
            json_array = json.loads(csv_file_to_json(options.data_file))
        else:
            with open(options.data_file, "r", encoding="utf-8") as f:
                json_array = json.load(f)
            logging.info("Loaded documents from the %s", options.data_file)

        for item in json_array:
            cmd = {"index": {"_index": options.index_name}}
            if "_id" in item:
                cmd["index"]["_id"] = item["_id"]

            upload_data_txt += json.dumps(cmd) + "\n"
            upload_data_txt += json.dumps(item) + "\n"

        if upload_data_txt:
            upload_batch(upload_data_txt)
    else:
        logging.info(
            "Generating %d docs, upload batch size is %d",
            options.count,
            options.batch_size,
        )

        for _ in range(0, options.count):
            item = generate_random_doc(fmt)

            if out_file:
                out_file.write(f"{json.dumps(item)}\n")

            cmd = {"index": {"_index": options.index_name}}
            if "_id" in item:
                cmd["index"]["_id"] = item["_id"]

            upload_data_txt += json.dumps(cmd) + "\n"
            try:
                upload_data_txt += json.dumps(item) + "\n"
            except Exception as e:
                print(item)
                raise e
            shared.UPLOAD_DATA_COUNT += 1

            if shared.UPLOAD_DATA_COUNT % options.batch_size == 0:
                upload_batch(upload_data_txt)
                upload_data_txt = ""

        # upload remaining items in `upload_data_txt`
        if upload_data_txt:
            upload_batch(upload_data_txt)

    if options.set_refresh:
        set_index_refresh("1s")

    if out_file:
        out_file.close()

    took_secs = int(time.time() - ts_start)

    logging.info(
        "Done - total docs uploaded: %d, took %d seconds",
        options.count,
        took_secs,
    )
