from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
import os
import re

## sam build && sam local invoke -e ./tests/cloudwatch-createloggroup-event.json CreateAOSIndexFunction

# Init Elasticsearch
session = boto3.Session()
credentials = session.get_credentials()
region = session.region_name

host = 'tr28xa0xlspn231i3jf7.us-east-1.aoss.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
service = os.environ['ES_SERVICE_NAME'] # 'aoss' for OpenSearch Serverless
index_prefix = os.environ['ES_INDEX_PREFIX']

auth = AWSV4SignerAuth(credentials, region, service)


# create an opensearch client and use the request-signer
es_client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20,
)


def lambda_handler(event, context):
    print('### EVENT:', event)
    log_group = event['detail']['requestParameters']['logGroupName']

    # Regular expression to match SageMaker training jobs or therwise, it should be an endpoint
    regex = r'sagemaker/TrainingJobs'
    # log_group_match = re.search(regex, log_group)

    if re.search(regex, log_group):
        # It is a SageMaker training job
        es_index = index_prefix + '-training'
    else:
        es_index = index_prefix + '-inference'

    print('\n### ES INDEX:', es_index)

    # Check whether the index exists in Elasticsearch
    indices_exists_response = es_client.indices.exists(es_index)
    print('\n### ES INDEX EXISTS:', indices_exists_response)

    # Create an index if it doesn't exist. If the index exists, do not create it again
    if not indices_exists_response:
        try:
            # create an index
            create_response = es_client.indices.create(
                es_index
            )
        
            print('\nCreating index:')
            print(create_response)
            return create_response
        
        except ConnectionError:
            print("Failed to connect to Elasticsearch cluster at", host)
            return {'Failed to connect to ' + host}
        
    else:
        return indices_exists_response

    