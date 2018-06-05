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
import logging
import json
import boto3
import os
import botocore
from botocore.vendored import requests

SUCCESS = 'SUCCESS'
FAILED = 'FAILED'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']

    logger.info(responseUrl)

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
#
# Inputs:
#     - assessment_template_arn (environment variable)
#     - assessment_notification_topic_arn (environment variable)
#
# Outputs:
#     - CloudWatch event notification
#==================================================
def lambda_handler(event, context):
    logger.info('CFN Event: {}'.format(json.dumps(event)))

    if 'assessment_template_arn' in os.environ:
        assessment_template_arn = os.environ['assessment_template_arn']
        logger.debug('assessment template arn: {}'.format(assessment_template_arn))
    else:
        raise

    if 'assessment_notification_topic_arn' in os.environ:
        assessment_notification_topic_arn = os.environ['assessment_notification_topic_arn']
        logger.debug('assessment_notification_topic_arn: {}'.format(assessment_notification_topic_arn))
    else:
        raise

    if 'RequestType' in event:

        if event['RequestType'] in ['Create', 'Update']:
            try:
                logger.info('CFN request type: {}'.format(event['RequestType']))

                client = boto3.client('inspector')

                # Add a notification for the assessment runs.
                logger.debug('Subscribing Inspector to CloudWatch event')
                logger.debug('resource arn: {}'.format(assessment_template_arn))
                logger.debug('event: ASSESSMENT_RUN_COMPLETED')
                logger.debug('topic arn: {}'.format(assessment_notification_topic_arn))

                response = client.subscribe_to_event(
                    resourceArn = assessment_template_arn,
                    event = 'ASSESSMENT_RUN_COMPLETED',
                    topicArn = assessment_notification_topic_arn
                )

                logger.info('Successfully subscribed Inspector to CloudWatch event')

            except botocore.exceptions.ClientError as e:
                logger.error('Failed to subscribe Inspector to CloudWatch event: {}'.format(e))

        elif event['RequestType'] in ['Delete']:
            pass # CloudFornmation will automatically delete this function

    send(event, context, SUCCESS, {"AssessmentTemplateArn":assessment_template_arn}, '')
    # JRS - I THINK ANYTHING BELOW THE SEND FUNCTION IS IGNORED
    #return {"AssessmentTemplateArn":assessment_template_arn}
