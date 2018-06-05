#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#  Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.   #
#                                                                            #
#  Licensed under the Amazon Software License (the "License"). You may not   #
#  use this file except in compliance with the License. A copy of the        #
#  License is located at                                                     #
#                                                                            #
#      http://aws.amazon.com/asl/                                            #
#                                                                            #
#  or in the "license" file accompanying this file. This file is distributed #
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,        #
#  express or implied. See the License for the specific language governing   #
#  permissions and limitations under the License.                            #
##############################################################################

#==================================================================================================
# Function: CreateSSMResourceSyncFunction
# Purpose:  Creates a resource data sync configuration to a single bucket in Amazon S3
#==================================================================================================

import logging
import json
import boto3
import os
import botocore
from botocore.vendored import requests


RESOURCE_SYNC_NAME = 'fleet-manager-resource-sync'
RESOURCE_SYNC_BUCKET_PREFIX = 'resource-sync'
SUCCESS = 'SUCCESS'
FAILED = 'FAILED'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']

    logger.info('ResponseURL: {}'.format(responseUrl))

    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData

    json_responseBody = json.dumps(responseBody)

    logger.info("Response body:\n" + json_responseBody)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }

    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        logger.info("Status code: " + response.reason)
    except Exception as e:
        logger.error("send(..) failed executing requests.put(..): " + str(e))

#==================================================
# Default handler
#==================================================
def lambda_handler(event, context):

    logger.info('CFN Event: {}'.format(json.dumps(event)))

    response_status = SUCCESS
    response_data = ''

    # Only execute in a custom CloudFormation resource creation or update event.
    if 'RequestType' in event:
        if event['RequestType'] in ['Create', 'Update']:
            try:
                resource_sync_exists = False # prove otherwise

                # First, determine whether the resource sync already exists.
                for resource_sync in boto3.client('ssm').list_resource_data_sync()['ResourceDataSyncItems']:
                    resource_sync_exists = resource_sync_exists or RESOURCE_SYNC_NAME == resource_sync['SyncName']

                logger.info('resource data sync {} exists: {}'.format(RESOURCE_SYNC_NAME, resource_sync_exists))

                # Create the resource sync if it doesn't already exist.
                if not resource_sync_exists:
                    logger.debug('resource sync does not exist')
                    logger.debug('resource sync name: {}'.format(RESOURCE_SYNC_NAME))
                    logger.debug('bucketname: {}'.format(os.environ['artifact_bucket_name']))
                    logger.debug('prefix: {}'.format(RESOURCE_SYNC_BUCKET_PREFIX))
                    logger.debug('sync format: JsonSerDe')
                    logger.debug('region: {}'.format(os.environ['AWS_REGION']))

                    response = boto3.client('ssm').create_resource_data_sync(
                        SyncName = RESOURCE_SYNC_NAME,
                        S3Destination = {
                            'BucketName': os.environ['artifact_bucket_name'],
                            'Prefix': RESOURCE_SYNC_BUCKET_PREFIX,
                            'SyncFormat': 'JsonSerDe',
                            'Region': os.environ['AWS_REGION']
                        }
                    )
                else:
                    logger.info('resource data sync exists.')

            except botocore.exceptions.ClientError as e:
                logger.error('Could not create the resource data sync: {}'.format(e))

        elif event['RequestType'] in ['Delete']:
            # This will be executed if the CloudFormation stack is being deleted.
            try:
                response = boto3.client('ssm').delete_resource_data_sync(
                    SyncName = RESOURCE_SYNC_NAME
                    )

            except botocore.exceptions.ClientError as e:
                logger.error('Could not delete the resource data sync: {}'.format(e))

    # Send the response to CloudFormation. Always send a success response;
    # otherwise, the CloudFormation stack execution will fail.
    send(event, context, response_status, {"Response":response_data}, '')
