#!/usr/bin/python
# -*- coding: utf-8 -*-
###################################################################################
#  Copyright 2018-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.   #
#                                                                                 #
#  Licensed under the Apache License, Version 2.0 (the "License").                #
#  You may not use this file except in compliance with the License.               #
#  A copy of the License is located at                                            #
#                                                                                 #
#      http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                                 #
#  or in the "license" file accompanying this file. This file is distributed      #
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either      #
#  express or implied. See the License for the specific language governing        #
#  permissions and limitations under the License.                                 #
###################################################################################

import logging
import json
import boto3
import os

from urllib import request, parse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('inspector')

def send(event, context, response_status, response_data):
    try:
        response_body = json.dumps({
            "Status": response_status,
            "Reason": 'See the details in CloudWatch Log Stream: {}'.format(context.log_stream_name),
            "PhysicalResourceId": context.log_stream_name,
            "StackId": event['StackId'],
            "RequestId": event['RequestId'],
            "LogicalResourceId": event['LogicalResourceId'],
            "Data": response_data
        })

        logger.info('Response URL: {}'.format(event['ResponseURL']))
        logger.info('Response Body: {}'.format(response_body))

        data = response_body.encode('utf-8')
        req = request.Request(event['ResponseURL'], data=data, method='PUT')
        req.add_header('Content-Type', '')
        req.add_header('Content-Length', len(response_body))
        response = request.urlopen(req)

        logger.info('Status code: {}'.format(response.getcode()))
        logger.info('Status message: {}'.format(response.msg))
    except Exception as e:
        logger.error('Custom resource send_response error: {}'.format(e))

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
        logger.error('No assessment_template_arn found.')
        send(event, context, 'FAILED', {"error": 'No assessment_template_arn found.'})
        return

    if 'assessment_notification_topic_arn' in os.environ:
        assessment_notification_topic_arn = os.environ['assessment_notification_topic_arn']
        logger.debug('assessment_notification_topic_arn: {}'.format(assessment_notification_topic_arn))
    else:
        logger.error('No assessment_notification_topic_arn found.')
        send(event, context, 'FAILED', {"error": 'No assessment_notification_topic_arn found.'})
        return

    try:
        if event['ResourceType'] == 'Custom::CreateInspectorResources' and event['RequestType'] in ['Create', 'Update']:
            logger.info('CFN request type: {}'.format(event['RequestType']))

            # Add a notification for the assessment runs.
            logger.debug('Subscribing Inspector to CloudWatch event')
            logger.debug('resource arn: {}'.format(assessment_template_arn))
            logger.debug('event: ASSESSMENT_RUN_COMPLETED')
            logger.debug('topic arn: {}'.format(assessment_notification_topic_arn))

            client.subscribe_to_event(
                resourceArn = assessment_template_arn,
                event = 'ASSESSMENT_RUN_COMPLETED',
                topicArn = assessment_notification_topic_arn
            )

            logger.info('Successfully subscribed Inspector to CloudWatch event')
    except Exception as e:
        logger.error('Failed to subscribe Inspector to CloudWatch event: {}'.format(e))

    send(event, context, 'SUCCESS', {"AssessmentTemplateArn": assessment_template_arn})
