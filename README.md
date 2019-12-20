# AWS Fleet Management at Scale
This solution helps customers more easily manage their fleet of servers,
automate software inventory management, OS patch compliance, and run security
vulnerability assessments. This solution uses AWS Systems Manager documents to enable
configuration as code to mange resources at scale. The document defines a
series of actions that allows you to remotely manage instances,
ensure desired state, and automate operations. If applicable, the solution also
uses Amazon Inspector to define the rules packages to be used in the assessments
and runs the assessments on a routine basis, reporting the findings to AWS Systems
Manager for the specific instance.

## Building the customized solution
* Clone the repository, then make the desired code changes.
```bash
git clone https://github.com/awslabs/server-fleet-management-at-scale.git
cd server-fleet-management-at-scale
export SFM_PATH=`pwd`
```

* Configure the build paraemters.
```bash
export DIST_OUTPUT_BUCKET=my-bucket-name # bucket where customized code will reside
export VERSION=my-version # version number for the customized code
export SOLUTION_NAME=server-fleet-management-at-scale # solution name for the customized code
```
_Note:_ You would have to create an S3 bucket with the prefix 'my-bucket-name-<aws_region>' as whole Lambda functions are going to get the source codes from the 'my-bucket-name-<aws_region>' bucket; aws_region is where you are deployting the customized solution (e.g. us-east-1, us-east-2, etc.).

* Build the customized solution
```bash
cd $SFM_PATH/deployment
chmod +x ./build-s3-dist.sh
./build-s3-dist.sh $DIST_OUTPUT_BUCKET $SOLUTION_NAME $VERSION
```

* Deploy the source codes to an Amazon S3 bucket in your account. _Note:_ You must have the AWS Command Line Interface installed and create the Amazon S3 bucket in your account prior to copy source codes.
```bash
export AWS_REGION=us-east-1 # the AWS region you are going to deploy the solution in your account.
export AWS_PROFILE=default # the AWS Command Line Interface profile

aws s3 cp $SFM_PATH/deployment/global-s3-assets/ s3://$DIST_OUTPUT_BUCKET-$AWS_REGION/$SOLUTION_NAME/$VERSION/ --recursive --acl bucket-owner-full-control --profile $AWS_PROFILE
aws s3 cp $SFM_PATH/deployment/regional-s3-assets/ s3://$DIST_OUTPUT_BUCKET-$AWS_REGION/$SOLUTION_NAME/$VERSION/ --recursive --acl bucket-owner-full-control --profile $AWS_PROFILE
```

## Deploying the customized solution
* Get the link of the server-fleet-management-at-scale.template uploaded to your Amazon S3 bucket.
* Deploy the Server Fleet Management at Scale solution to your account by launching a new AWS CloudFormation stack using the link of the server-fleet-management-at-scale.template.

***

Copyright 2018-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://www.apache.org/licenses/LICENSE-2.0

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
