# OpenSearch : Generate and Upload Randomized Test Data

Because everybody loves test data.

## Ok, so what is this thing doing?

`opensearch_test.py` lets you generate and upload randomized test data and queries, see what performance is like, and verify your cluster is able to handle the load.

It allows for easy configuring of what the test documents look like, what kind of data types they include and what the field names are called.

## File Descriptions

- **requirements.txt**: Lists the Python dependencies required to run the test script.
- **modules** Folder: Modularized python fuctions.
- **opensearch_test.py**: The main Python script that performs the OpenSearch tests.
- **LICENSE**: License
- **Dockerfile**: Contains the instructions to build the Docker image for the test environment.

## Before Using it

### Change Server Config

Recommended method for Config is create `server.conf` file and input the values needed.

If you are not using a config file, you need to pass the required values as `arguments`.

However, when there are many values to set, it is much more convenient to create and use a `server.conf` file.

Enter the desired options in the `server.conf` file.

Example:

Create the configure file

```shell
cd ${REPO}
touch server.conf
${EDITOR} server.conf
```

Edit configure file

### Basic configure file example

```conf
# server.conf
action = "all"
opensearch_url = "https://uri.for.opensearch.db:port"
username = "./client_cert.pem"
password = "./client_key.pem"
```

### What can be configure?

| Setting                 | Description                                                            | Default Value           |
| ----------------------- | ---------------------------------------------------------------------- | ----------------------- |
| action                  | Specify the action to be performed.                                    | all                     |
| json_path               | Query JSON file path                                                   | None                    |
| batch_size              | OpenSearch bulk index batch size                                       | 1000                    |
| client_cert             | Filepath of CA certificates in PEM format                              | None                    |
| client_key              | Filepath of client SSL key                                             | None                    |
| count                   | Number of docs to generate                                             | 100000                  |
| data_file               | Name of the documents file to use                                      | None                    |
| dict_file               | Name of dictionary file to use                                         | None                    |
| finish_time             | Shape Finish Time in '%Y-%m-%d %H:%M:%S' format                        | None                    |
| force_init_index        | Force deleting and re-initializing the OpenSearch index                | False                   |
| format                  | Message format                                                         | (truncated for brevity) |
| http_upload_timeout     | Timeout in seconds when uploading data                                 | 10                      |
| id_type                 | Type of 'id' to use for the docs, int or uuid4                         | None                    |
| index_name              | Name of the index to store your messages                               | test                    |
| index_type              | Index type                                                             | test_type               |
| number_of_replicas      | Number of replicas for OpenSearch index                                | 1                       |
| number_of_shards        | Number of shards for OpenSearch index                                  | 1                       |
| opensearch_url          | URL of your OpenSearch node                                            | http://localhost:9200   |
| out_file                | Write test data to out_file as well                                    | False                   |
| password                | Password for OpenSearch                                                | None                    |
| random_seed             | Random seed number for Faker                                           | None                    |
| set_refresh             | Set refresh rate to -1 before starting the upload                      | False                   |
| start_time              | Shape Start Time in '%Y-%m-%d %H:%M:%S' format                         | None                    |
| username                | Username for OpenSearch                                                | None                    |
| validate_cert           | SSL validate_cert for requests. Use false for self-signed certificates | True                    |

Main configuration values are as follows.

- `action`: [generate_data, query_all, custom_query, delete_index, all] choose one
  - generate_data: upload the data generated through `format` to the OpenSearch database.
  - query_all: request all values of the specified index within the range using `start_time` and `finish_time`.
  - custom_query: You can specify the values for the body used in the request through a JSON file. this option require `json_path`. For more [read docs](https://opensearch.org/docs/latest/api-reference/search/)
  - delete_index: All data at the specified index will be deleted. (Please use with caution.)
  - all: I will conduct whole process test.(generate_data -> query_all -> delete_index)
- `start_time` and `finish_time`: If values are `None`, they will default to 30 days before and 30 days after the current time.
- The values that need to be set according to the server's security settings are as follows:
  - `validate_cert`
  - `client_cert`
  - `client_key`
  - `username`
  - `password`
- `format`: See this section [Generate Custom Document format](#generate-custom-document-format)
- `random_seed`: Most of the values are generated using the `Faker` library. This value is a random seed number used for that.
- `count` and `batch_size`: `count` represents the total number of docs to be generated, while the `batch_size` specifies the number of docs that uploaded at once.

### Generate Custom Document format

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
- `arr:[array_length_expression]:[single_element_format]` an array of entries with format specified by `single_element_format`.  `array_length_expression` can be either a single number, or pair of numbers separated by `-` (i.e. 3-7), defining range of lengths from with random length will be picked for each array (Example `int_array:arr:1-5:int:1:250`)
- `log_version` a random version `str` looks like v1.1.1
- `sha` generate random sha(len 40)
- `file_name` Generate fake python file(.py)
- `uuid` Generate fake uuid
- `service` Generate fake service name

for more read this github repo [README.md](https://github.com/obazda20/opensearch-test-data?tab=readme-ov-file#what-about-the-document-format) file

## Testing Methods

Testing can be run either use `Docker` or run the `Python` file directly.

### Using Docker

`Docker` must be installed, and you need to have an internet connection.  

Follow [Install Docker Engine](https://docs.docker.com/engine/install/)

Do not forgot to mount all files using -v when running `docker run`.

```shell
cd ${REPO}
docker build -t <docker_image_name>:<tag> .
docker run -v ${PWD}/client_cert.pem:/app/client_cert.pem -v ${PWD}/client_key.pem:/app/client_key.pem -v /server.conf:/app/server.conf <docker_image_name>:<tag>
```

### Using python

[python3](https://www.python.org/downloads/) needs to be installed.

Dependencies can be installed from `requirements.txt`.

Example:

```shell
# install requirements
pip install --no-cache-dir -r requirements.txt
```

After the installation of dependencies is complete, you should check if the required file paths are set correctly, and then you can run it as follows.

Please check if the following files are properly configured before execution.

- server.conf
- client_cert.pem(optional)
- client_key.pem(optional)
- custom_query_json_file(optional)

```shell
# run script
python opensearch_test.py
```

## Result Example

```bash
[I 241114 10:42:31 opensearch_test:47] ***Start Data Generate Test***
[I 241114 10:42:32 requests:83] Trying to create index https://db.test.co.kr/test
[I 241114 10:42:33 requests:89] Looks like the index exists already
[I 241114 10:42:33 upload_data:83] Generating 20000 docs, upload batch size is 10000
[I 241114 10:42:55 requests:109] Upload: OK - upload took:  4551ms, total docs uploaded:   10000
[I 241114 10:43:18 requests:109] Upload: OK - upload took:  4598ms, total docs uploaded:   20000
[I 241114 10:43:18 upload_data:123] Done - total docs uploaded: 20000, took 45 seconds
[I 241114 10:43:18 opensearch_test:52] ***Start Query All Test***
[I 241114 10:43:41 requests:226] Total hits: 1022000, Total pages: 103
[I 241114 10:43:44 requests:231] Retrieved page 1 of 103
[I 241114 10:43:48 requests:231] Retrieved page 2 of 103
...
[I 241114 10:50:08 requests:231] Retrieved page 103 of 103
[I 241114 10:50:09 requests:213] Scroll context cleared successfully
[I 241114 10:50:09 requests:235] Total Querying time taken: 13116.00ms
[I 241114 10:50:09 opensearch_test:62] ***Start Period Breakdown Query test***
[I 241114 10:50:10 requests:293] Total Querying time taken: 376ms
[I 241114 10:50:10 opensearch_test:67] ***Start Delete Index***
[I 241114 10:50:13 requests:61] Deleting index 'test' done b'{"acknowledged":true}'
```

Through this test, you can verify whether OpenSearch is functioning properly.

You can also check the performance.
