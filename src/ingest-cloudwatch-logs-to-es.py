'''
The Lambda function collect data from CloudWatch logs subscription filter and ingest filtered logs into an Elasticsearch index.
Runtime: Python 3.8-

The Lambda function requires some dependencies to be installed manually. They are: requests, opensearchpy, and requests_aws4auth
'''

import boto3
from botocore.exceptions import ClientError
import json
import os

# OpenSearch Serverless dependencies
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

# Handle compression
import base64
import zlib

# Convert base64 encoded gzip string to JSON
def gzip_to_json(gzip_str):

    # Convert base64 encoded string back to bytes
    base64decoded_str = base64.b64decode(gzip_str.encode('utf-8'))

    # Decompress bytes to bytes
    decompressed_data=zlib.decompress(base64decoded_str, 16+zlib.MAX_WBITS)

    if decompressed_data:
        json_data = json.loads(decompressed_data)

    return json_data

# Init Elasticsearch
session = boto3.Session()
credentials = session.get_credentials()
region = session.region_name

es_host = os.environ['ES_HOST'] # OpenSearch serverless host doesn't have the HTTPS prefix. cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com

es_index = 'sagemaker-log-inference'
doctype = '_doc'
headers = { "Content-Type": "application/json" }
service = os.environ['ES_SERVICE_NAME']

auth = AWSV4SignerAuth(credentials, region, service)

# Create an opensearch client and use the request-signer
es_client = OpenSearch(
    hosts=[{'host': es_host, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20,
)


# Post a line of log to Elasticsearch
def post_log_to_elasticsearch(log):
    document = log
    print('### EVENT:', document)

    # Check whether the index exists in Elasticsearch
    indices_exists_response = es_client.indices.exists(es_index)
    print('### ES INDEX EXISTS:', indices_exists_response)
    
    # Create an index if it doesn't exist. If the index exists, do not create it again
    if not indices_exists_response:
        # create an index
        create_response = es_client.indices.create(
            es_index
        )
    
        print('\nCreating index:')
        print(create_response)

    # Index a document - use log timestamp + 3 digits random int  as the document ID
    response = es_client.index(
        index = es_index,
        body = document,
        id = document['timestamp'],
        refresh = False
    )
    print('\n INDEX DOCUMENT:', response)

    # Check the response from OpenSearch
    if response['result'] == 'created' or response['result'] == 'updated':
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Document indexed successfully."})
        } 
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error indexing document.", "error": response})
        }


'''
A function accepts a JSON list and bulk ingest to Elasticsearch

Example: movies = '{ "index" : { "_index" : "my-dsl-index", "_id" : "2" } } \n { "title" : "Interstellar", "director" : "Christopher Nolan", "year" : "2014"} \n { "create" : { "_index" : "my-dsl-index", "_id" : "3" } } \n { "title" : "Star Trek Beyond", "director" : "Justin Lin", "year" : "2015"} \n { "update" : {"_id" : "3", "_index" : "my-dsl-index" } } \n { "doc" : {"year" : "2016"} }'
'''
def bulk_ingest_to_elasticsearch(es_metadata, log_json):
    # Create the bulk request body
    bulk_body = []

    # construct a Elasticsearch bulk data
    for log_obj in log_json:
        # Filter based on log messages
        # ...

        # Add the index metadata to bulk_body
        bulk_body.append(json.dumps({ "create": { "_index": es_index, "_id": log_obj['timestamp']}}))

        # Merge list log_obj to list aes_log. 
        aes_log = es_metadata
        aes_log = {**aes_log, **log_obj}
         
        # Merge list log_obj to list aes_log. 
        print('### AES LOG:', aes_log)
        bulk_body.append(json.dumps(aes_log))

    # Convert the bulk_body into a Elasticsearch bulk operation one line string
    bulk_body_str = ' \n '.join(bulk_body)
    print('\n### BULK STR:', bulk_body_str)

    # Bulk index documents - use log timestamp + 3 digits random int  as the document ID
    try: 
        response = es_client.bulk(bulk_body_str)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Documents bulk indexed successfully."})
        } 
    except ConnectionError:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error bulk indexing documents.", "error": response})
        }


# Filter logs based on log message
def cloudwatch_log_filter(log):
     return False


# Create CloudWatchLogs client
cloudwatch_logs = boto3.client('logs')

# Test sam local invoke
## sam build && sam local invoke -e ./tests/events/cloudwatch-logstream-raw-base64.json SubscriptionFilterIngestLogToAOSFunction

def lambda_handler(event, context):
    # Get CloudWatch logs and run base64 decoding and unzip
    log_json = gzip_to_json(event['awslogs']['data'])

    # Determine whether it's a inference or training log
    if 'logGroup' in log_json and "sagemaker/Endpoints/" in log_json['logGroup']:
        log_type = "inference"
    else:
        log_type = "training"

    # Construct the common metadata for each Elastisearch document
    es_metadata = {
        'owner': log_json['owner'],
        'logGroup': log_json['logGroup'],
        'logStream': log_json['logStream'],
        'subscriptionFilters': log_json['subscriptionFilters'],
        'log_type': log_type
    }
    print('### METADATA:', es_metadata)

    # Bulk ingest method
    # bulk_ingest_to_elasticsearch(es_metadata, log_json['logEvents'])
    # quit()

    for log_obj in log_json['logEvents']:
        # Filter based on log messages

        # Merge list log_obj to list aes_log. 
        aes_log = es_metadata
        aes_log = {**aes_log, **log_obj}
         
        # Merge list log_obj to list aes_log. 
        print('### AES LOG:', aes_log)

        # Add the aes_log as a document into Elasticsearch index.
        es_result = post_log_to_elasticsearch(aes_log)
        print('### ES RESULT:', es_result)
