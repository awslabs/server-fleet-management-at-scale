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

## OS/Python Environment Setup
```bash
yum update -y
yum install zip -y
```

## Building Lambda Package
```bash
cd deployment
./build-s3-dist.sh source-bucket-base-name version
```
source-bucket-base-name should be the base name for the S3 bucket location where the template will source the Lambda code from.
The template will append '-[region_name]' to this value.
For example: ./build-s3-dist.sh solutions v1.0
The template will then expect the source code to be located in the solutions-[region_name] bucket

## CF template and Lambda functions
Located in deployment/dist


***

Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/asl/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.
