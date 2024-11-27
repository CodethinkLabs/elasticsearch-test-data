# Elasticsearch For Beginners: Generate and Upload Randomized Test Data

Because everybody loves test data.

## Ok, so what is this thing doing?

`search_test.py` lets you generate and upload randomized test data to
your Elasticsearch or Opensearch cluster so you can start running queries, see what performance
is like, and verify your cluster is able to handle the load.

It allows for easy configuring of what the test documents look like, what
kind of data types they include and what the field names are called.

## Cool, how do I use this?

### Run Python script

Let's assume you have an Elasticsearch or Opensearch cluster running.

Python, [Tornado](https://github.com/tornadoweb/tornado/) and [Faker](https://github.com/joke2k/faker) are used. Run
`pip install tornado` and `pip install Faker` to install if you don't have them already.

It's as simple as this:

```text
$ python3 search_test.py

***Start Data Generate Test***
Trying to create index http://localhost:9200/test_data
Creating index test_data done   {'acknowledged': True, 'shards_acknowledged': True, 'index': 'test_data'}
Generating 2000 docs, upload batch size is 1000
Upload: OK - upload took:   412ms, total docs uploaded:    1000
Upload: OK - upload took:   197ms, total docs uploaded:    2000
Done - total docs uploaded: 2000, took 1 seconds
***Start Query All Test***
Total hits: 2000, Total pages: 1
Retrieved page 1 of 1
Scroll context cleared successfully
Total Querying time taken: 85.00ms
***Start Delete Index***
Deleting index 'test_data' done
```

Without any command line options, it will generate and upload 1000 documents
of the format

```json
{
    "name":<<str>>,
    "age":<<int>>,
    "@timestamp":<<tstxt>>
}
```

to an Elasticsearch cluster at `http://localhost:9200` to an index called
`test_data`.

### Docker and Docker Compose

Requires [Docker](https://docs.docker.com/get-docker/) for running the app and [Docker Compose](https://docs.docker.com/compose/install/) for running a single ElasticSearch domain with two nodes (es1 and es2).

1. Set the maximum virtual memory of your machine to `262144` otherwise the ElasticSearch instances will crash, [see the docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html)
    ```bash
    $ sudo sysctl -w vm.max_map_count=262144
    ```
1. Clone this repository
    ```bash
    $ git clone <change_this_to_repository_url>
    $ cd elasticsearch-test-data
    ```
1. Run the ElasticSearch stack
    ```bash
    $ docker-compose up --detached
    ```
1. Run the app and inject random data to the ES stack
    ```bash
    $ docker run --rm -it --network host oliver006/es-test-data  \
        --es_url=http://localhost:9200  \
        --batch_size=10000  \
        --username=elastic \
        --password="esbackup-password"
    ```
1. Cleanup
    ```bash
    $ docker-compose down --volumes
    ```

## Not bad but what can I configure?

`python search-test.py --help` also gives you the full set of command line options,  
here are more description about the most important ones:

- `action`: [generate_data, query_all, custom_query, delete_index, all] choose one
  - generate_data: upload the data generated through `format` to the OpenSearch database.
  - query_all: request all values of the specified index within the range using `start_time` and `finish_time`. For this test, you need to generate time data using `@timestamp` for it to be callable. If you don't want to use that key, use `custom_query`.
  - custom_query: You can specify the values for the body used in the request through a JSON file. this option require `json_path`. For more information read the api documentation - [ElasticSearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html#run-an-es-search) [OpenSearch](https://opensearch.org/docs/latest/api-reference/search/)
  - delete_index: All data at the specified index will be deleted. (Please use with caution.)
  - all: (default) Conduct whole process test.(generate_data -> query_all -> delete_index)
- For authentication to the server, the following options are available:
  - `validate_cert` : SSL validate_cert for requests. Use false for self-signed certificates
  - Certificate based auth:
    - `client_cert` : filepath of CA certificates in PEM format
    - `client_key` : filepath of for client SSL key
  - Username based auth:
    - `username` : the username when basic auth is required
    - `password` : the password when basic auth is required
- `--search_db_url=http://localhost:9200` the base URL of your search DB node, don't include the index name
- `--count=###` number of documents to generate and upload
- `--index_name=test_data` the name of the index to upload the data to.
  If it doesn't exist it'll be created with these options
  - `--num_of_shards=2` the number of shards for the index
  - `--num_of_replicas=0` the number of replicas for the index
- `--batch_size=###` we use bulk upload to send the docs to DB, this option controls how many we send at a time
- `--force_init_index=False` if `True` it will delete and re-create the index
- `--dict_file=filename.dic` if provided the `dict` data type will use words
  from the dictionary file, format is one word per line. The entire file is
  loaded at start-up so be careful with (very) large files.
- `--data_file=filename.json|filename.csv` if provided all data in the filename will be inserted into es. The file content has to be an array of json objects (the documents). If the file ends in `.csv` then the data is automatically converted into json and inserted as documents.

### All configuration

| Setting                 | Description                                                            | Default Value           |
| ----------------------- | ---------------------------------------------------------------------- | ----------------------- |
| action                  | Specify the action to be performed.                                    | all                     |
| json_path               | Query JSON file path                                                   | None                    |
| batch_size              | bulk index batch size                                                  | 1000                    |
| client_cert             | Filepath of CA certificates in PEM format                              | None                    |
| client_key              | Filepath of client SSL key                                             | None                    |
| count                   | Number of docs to generate                                             | 1000                    |
| data_file               | Name of the documents file to use                                      | None                    |
| dict_file               | Name of dictionary file to use                                         | None                    |
| finish_time             | Shape Finish Time in '%Y-%m-%d %H:%M:%S' format                        | None                    |
| force_init_index        | Force deleting and re-initializing the index                           | False                   |
| format                  | Message format                                                         | (truncated for brevity) |
| http_upload_timeout     | Timeout in seconds when uploading data                                 | 10                      |
| id_type                 | Type of 'id' to use for the docs, int or uuid4                         | None                    |
| index_name              | Name of the index to store your messages                               | test_data                    |
| index_type              | Index type                                                             | test_type               |
| number_of_replicas      | Number of replicas                                                     | 1                       |
| number_of_shards        | Number of shards                                                       | 1                       |
| search_db_url           | URL of your DB                                                         | http://localhost:9200   |
| out_file                | Write test data to out_file as well                                    | False                   |
| password                | Password for DB                                                        | None                    |
| random_seed             | Random seed number for Faker                                           | None                    |
| set_refresh             | Set refresh rate to -1 before starting the upload                      | False                   |
| start_time              | Shape Start Time in '%Y-%m-%d %H:%M:%S' format                         | None                    |
| username                | Username for DB                                                        | None                    |
| validate_cert           | SSL validate_cert for requests. Use false for self-signed certificates | True                    |

### How to setup config file

Recommended method for Config is create `server.conf` file and input the values needed.

However, when there are many values to set, it is much more convenient to create and use a `server.conf` file.

Enter the desired options in the `server.conf` file.

Example:

Create the configure file

```shell
cd ${REPOSITORY}/elasticsearch-test-data
touch server.conf
${EDITOR} server.conf
```

Edit configure file

```conf
# server.conf
action = "all"
opensearch_url = "https://uri.for.search.db:port"
username = TEST_NAME
password = TEST_PASSWORD
```

### What about the document format?

Glad you're asking, let's get to the doc format.

The doc format is configured via `--format=<<FORMAT>>` with the default being
`name:str,age:int,@timestamp:tstxt`.

The general syntax looks like this:

`<<field_name>>:<<field_type>>,<<field_name>>::<<field_type>>, ...`

For every document, `search_test.py` will generate random values for each of
the fields configured.

Currently supported field types are:

- `bool` returns a random true or false
- `ts` a timestamp (in milliseconds), randomly picked between now +/- 30 days
- `ipv4` returns a random ipv4
- `tstxt` a timestamp in the "%Y-%m-%dT%H:%M:%S.000-0000" format, randomly
  picked between now +/- 30 days
- `int:min:max` a random integer between `min` and `max`. If `min` and `max`
  are not provided they default to 0 and 100000
- `str:min:max` a word ( as in, a string), made up of `min` to `max` random
  upper/lowercase and digit characters. If `min` and `max` are optional,
  defaulting to `3` and `10`
- `words:min:max` a random number of `strs`, separated by space, `min` and
  `max` are optional, defaulting to '2' and `10`
- `dict:min:max` a random number of entries from the dictionary file,
  separated by space, `min` and `max` are optional, defaulting to '2' and `10`
- `text:words:min:max` a random number of words seperated by space from a
  given list of `-` seperated words, the words are optional defaulting to
  `text1` `text2` and `text3`, min and max are optional, defaulting to `1`
  and `1`
- `arr:[array_length_expression]:[single_element_format]` an array of entries
  with format specified by `single_element_format`. `array_length_expression`
  can be either a single number, or pair of numbers separated by `-` (i.e. 3-7),
  defining range of lengths from with random length will be picked for each array
  (Example `int_array:arr:1-5:int:1:250`)
- `log_version` a random version `str` looks like v1.1.1
- `sha` generate random sha(len 40)
- `file_name` Generate fake file `file_name:.py`  
- `uuid` Generate fake uuid
- `systemd` Generate fake systemd name

## Todo

- more different format types
- ...

All suggestions, comments, ideas, pull requests are welcome!
