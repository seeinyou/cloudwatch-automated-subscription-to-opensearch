########################################################################################
# Version - 1.0
# Description - This lambda Function code can read event when a new logGroup is created and
# automatically subscribes it to Target (OpenSearch)
########################################################################################

import boto3
import os

# Evironment variables
target_lambda_func_arn = os.environ['TARGET_LAMBDA_FUNCTION_ARN']
cloudwatch_filter_name = os.environ['CLOUDWATCH_FILTER_NAME']
cloudwatch_fitler_pattern = os.environ['CLOUDWATCH_FILTER_PATTERN']

# Create CloudWatchLogs client
cloudwatch_logs = boto3.client('logs')

def lambda_handler(event, context):
    # Read logGroup name from the CreateLogGroup event triggered when new log group created
    log_group_to_subscribe = event['detail']['requestParameters']['logGroupName']
    print("The name of Log Group to subscribe ::",log_group_to_subscribe)

    LAMBDA_FUNCTION_ARN = target_lambda_func_arn
    FILTER_NAME = cloudwatch_filter_name
    LOG_GROUP = log_group_to_subscribe

    # Use the pattern '[ type = task*, uname, ... ]' Only pass log strings begins with "task"
    filter_pattern = cloudwatch_fitler_pattern

    # Create a subscription filter
    cloudwatch_logs.put_subscription_filter(
        destinationArn=LAMBDA_FUNCTION_ARN,
        filterName= FILTER_NAME,
        filterPattern=filter_pattern,
        logGroupName=LOG_GROUP,
    )