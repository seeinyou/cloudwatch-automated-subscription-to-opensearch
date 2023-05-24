# Automatic CloudWatch Log Group Subscription to Amazon OpenSearch
This repository contains code that automatically creates a CloudWatch log group Lambda subscription when it is created. The Lambda function enables CloudWatch logs to be transferred to an Amazon OpenSearch serverless collection, which comes with an OpenSearch dashboard. This can be useful for monitoring and analyzing logs in real-time, especially for Amazon SageMaker inference and training logs.

## Requirements

To use this code, you will need:

- An AWS account
- The AWS CLI installed and configured
- The AWS Serverless Application Model (SAM) CLI installed
- An Amazon OpenSearch domain [optional]

## Installation
1. Clone the repository to your local machine: git clone https://github.com/username/repository.git
2. Navigate to the repository directory: cd repository
3. Build the SAM package using the SAM CLI: sam build
4. Deploy the SAM stack using the SAM CLI: sam deploy --guided
5. Follow the prompts to configure the stack. You will need to provide the name of your Amazon OpenSearch domain, as well as the name of the CloudWatch log group that you want to subscribe to.

## Usage
Once the SAM stack is deployed, the Lambda function will automatically create a subscription filter for the specified CloudWatch log group. The filter will forward any logs to the specified Amazon OpenSearch domain.

To view the logs in the OpenSearch dashboard, navigate to the Kibana endpoint for your domain and select the "Discover" tab. You should see alist of all the logs that have been forwarded from the CloudWatch log group.

## Configuration
If you want to customize the Lambda function or the AWS SAM stack, you can modify the code in the template.yaml file and rebuild the stack using the SAM CLI.

The Lambda function code is located in the **src/** directory. You can modify this code to change the behavior of the function, such as filtering specific log events or transforming the data before sending it to OpenSearch.

## License
This code is licensed under the Apache 2.0 license. For more information, see the LICENSE file.

## Contributions
Contributions to this code are welcome. If you want to contribute, please fork the repository and submit a pull request with your changes.