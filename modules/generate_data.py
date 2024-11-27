"""
This module handles functions that generate Fake data
"""

# pylint: disable=E0401
import csv
from datetime import datetime, timedelta
import json
import random
import string
import uuid

from tornado.options import options

from . import shared
from .faker import fake


def get_data_for_format(fmt):
    """
    split 'format' and gives to proper fuctions
    """

    split_f = fmt.split(":")
    if not split_f:
        return None, None

    # Variables
    return_val = ""

    type_handlers = {
        "arr": array_generate,
        "bool": bool_generate,
        "str": str_generate,
        "int": int_generate,
        "ipv4": ipv4_generate,
        "ts": ts_generate,
        "tstxt": ts_generate,
        "words": words_generate,
        "dict": dict_generate,
        "text": text_generate,
        "log_version": log_version_generate,
        "sha": sha_generate,
        "file_name": generate_filename,
        "uuid": generate_uuid,
        "systemd": generate_systemd,
    }

    handler = type_handlers.get(split_f[1])

    if handler:
        return_val = handler(fmt)

    return split_f[0], return_val


def set_start_time():
    """
    This fuctions is used to wcreate start time for default
    """
    if options.start_time is None:
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        return thirty_days_ago.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    return change_datetime_to_iso8601_str(options.start_time)


def set_finish_time():
    """
    This fuctions is used to create finish time for default
    """
    if options.start_time is None:
        now = datetime.now()
        thirty_days_later = now + timedelta(days=30)
        return thirty_days_later.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    return change_datetime_to_iso8601_str(options.finish_time)


def convert_string_to_datetime(date_string):
    """
    string time to datetime
    """
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.000Z")


def change_datetime_to_iso8601_str(time_str):
    """
    Parses the input string into a datetime
    object and outputs it in ISO 8601 format
    """
    date_time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

    return date_time_obj.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def generate_count(min_value, max_value):
    """
    This Function Generate Count using Faker
    """
    return fake.random_int(min=min_value, max=max_value)


def split_fmt(fmt):
    """
    split format argument
    """
    split_f = fmt.split(":")
    field_name = split_f[0]
    field_type = split_f[1]

    return (split_f, field_name, field_type)


def array_generate(fmt):
    """
    generate random array
    """
    split_f, field_name, field_type = split_fmt(fmt)
    value = []
    array_len_expr = split_f[2]
    if "-" in array_len_expr:
        (min_value, max_value) = array_len_expr.split("-")
        array_len = generate_count(int(min_value), int(max_value))
    else:
        array_len = int(array_len_expr)

    single_elem_format = (
        field_name
        + ":"
        + fmt[len(field_name) + len(field_type) + len(array_len_expr) + 3:]
    )
    for _ in range(array_len):
        x = get_data_for_format(single_elem_format)
        value.append(x[1])
    return value


def bool_generate(_):
    """
    generate random boolean
    """
    return fake.boolean()


def str_generate(fmt):
    """
    str:min:max a word, made up of min to max random upper/lowercase and digit
    """
    split_f, _, _ = split_fmt(fmt)
    min_value = 3 if len(split_f) < 3 else int(split_f[2])
    max_value = min_value + 7 if len(split_f) < 4 else int(split_f[3])
    length = generate_count(min_value, max_value)

    return fake.bothify(fake.random_bothify_pattern(length))


def int_generate(fmt):
    """
    generate a random integer between min and max (int:min:max)
    """
    split_f, _, _ = split_fmt(fmt)
    min_value = 0 if len(split_f) < 3 else int(split_f[2])
    max_value = min_value + 100000 if len(split_f) < 4 else int(split_f[3])
    return_val = generate_count(min_value, max_value)

    return return_val


def ipv4_generate(_):
    """
    generate a fake ip
    """
    return fake.ipv4()


def ts_generate(fmt):
    """
    generate a timestamp (in milliseconds) or
    timestamp in the "%Y-%m-%dT%H:%M:%S.000Z" format
    """

    _, _, field_type = split_fmt(fmt)

    min_value = set_start_time()
    max_value = set_finish_time()

    random_timestamp = fake.date_time_between_dates(
        datetime_start=convert_string_to_datetime(min_value),
        datetime_end=convert_string_to_datetime(max_value),
    ).timestamp()

    return_val = (
        int(random_timestamp * 1000)
        if field_type == "ts"
        else datetime.fromtimestamp(random_timestamp).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
    )
    return return_val


def words_generate(fmt):
    """
    Generate random number of strs, separated by space
    """
    split_f, _, _ = split_fmt(fmt)

    min_value = 2 if len(split_f) < 3 else int(split_f[2])
    max_value = min_value + 8 if len(split_f) < 4 else int(split_f[3])
    count = generate_count(min_value, max_value)

    words = []
    for _ in range(count):
        word_len = random.randrange(3, 10)
        word = "".join(
            fake.random_element(elements=string.ascii_letters + string.digits)
            for _ in range(word_len)
        )
        words.append(word)

    return " ".join(words)


def dict_generate(fmt):
    """
    Generate a random number of entries from the dictionary file
    """
    split_f, _, _ = split_fmt(fmt)

    min_value = 2 if len(split_f) < 3 else int(split_f[2])
    max_value = min_value + 8 if len(split_f) < 4 else int(split_f[3])
    count = generate_count(min_value, max_value)

    return " ".join(
        [
            fake.random_element(elements=shared.DICT_DATA).strip()
            for _ in range(count)
        ]
    )


def text_generate(fmt):
    """
    generate random number of words seperated
    by space from a given list of - seperated words
    """
    split_f, _, _ = split_fmt(fmt)

    text = (
        ["text1", "text2", "text3"]
        if len(split_f) < 3
        else split_f[2].split("-")
    )
    min_value = 1 if len(split_f) < 4 else int(split_f[3])
    max_value = min_value + 1 if len(split_f) < 5 else int(split_f[4])
    count = generate_count(min_value, max_value)
    words = []
    for _ in range(count):
        words.append("" + random.choice(text))
    return_val = " ".join(words)

    return return_val


def log_version_generate(_):
    """
    Generate fake version string
    """
    major = fake.random_int(min=0, max=9)
    minor = fake.random_int(min=0, max=99)
    patch = fake.random_int(min=0, max=99)
    return f"v{major}.{minor}.{patch}"


def sha_generate(_):
    """
    Generate fake sha hash string
    """
    return fake.sha1()


def generate_filename(fmt):
    """
    Generate fake file
    default extention ".py"
    """
    split_f, _, _ = split_fmt(fmt)

    if len(split_f) == 2:
        extention = "py"
    else:
        extention = split_f[2]

    return fake.file_name(extension=f".{extention}")


def generate_uuid(_):
    """
    Generate fake uuid
    """
    return fake.uuid4()


def generate_random_doc(fmt):
    # pylint: disable=global-statement
    """
    This Function Generate Random Data
    """

    res = {}

    for f in fmt:
        f_key, f_val = get_data_for_format(f)
        if f_key:
            res[f_key] = f_val

    if not options.id_type:
        return res

    if options.id_type == "int":
        res["_id"] = shared.ID_COUNTER

        shared.ID_COUNTER += 1
    elif options.id_type == "uuid4":
        res["_id"] = str(uuid.uuid4())

    return res


def generate_systemd(_):
    """
    Generate a random service name.
    """

    suffixes = [
        "service",
        "socket",
        "target",
        "device",
        "mount",
        "automount",
        "swap",
        "timer",
        "path",
        "slice",
        "scope",
    ]

    random_words = [fake.word() for _ in range(3)]
    suffix = random.choice(suffixes)

    return f"{'-'.join(random_words)}.{suffix}"


def csv_file_to_json(csv_file_path):
    """
    Change CSV file to JSON file
    """
    data = []

    with open(csv_file_path, encoding="utf-8") as csvf:
        csv_reader = csv.DictReader(csvf)
        for rows in csv_reader:
            data.append(rows)

    return json.dumps(data)
