#!/usr/bin/python
# -*- coding: utf-8 -*-
###################################################################################
#  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.        #
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
import boto3
import json
import urllib
import uuid

from urllib import request
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client('ec2')

# Send anonymous metric function
def send_anonymous_metric(solution_id, solution_version, solution_uuid, region, event_type):
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    metric_url = 'https://metrics.awssolutionsbuilder.com/generic'
    response_body = json.dumps({
        "Solution": solution_id,
        "UUID": solution_uuid,
        "TimeStamp": now,
        "Data": {
            "Launch": now,
            "Region": region,
            "Version": solution_version,
            "EventType": event_type
        }
    })
    logger.info('Metric Body: {}'.format(response_body))

    try:
        data = response_body.encode('utf-8')
        req = request.Request(metric_url, data=data)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Content-Length', len(response_body))
        response = request.urlopen(req)

        logger.info('Status code: {}'.format(response.getcode()))
        logger.info('Status message: {}'.format(response.msg))
    except Exception as e:
        logger.error('Error occurred while sending metric: {}'.format(json.dumps(response_body)))
        logger.error('Error: {}'.format(e))

# Send response function
def send_response(event, context, response_status, response_data):
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

#  A sample function that looks up the latest AMI ID for a given region and ami name.
def get_ami_info(ami_name):
    try:
        logger.info('Calling describe_images...')
        response = ec2.describe_images(
            Filters=[
                {
                    "Name": "name",
                    "Values": [
                        ami_name
                    ]
                }
            ]
        )
        logger.info('Got a response back from the server')

        # Sort images by name in decscending order. The names contain the AMI version, formatted as YYYY.MM.Ver.
        images = sorted(response['Images'], key=lambda k: k['CreationDate'], reverse=True)
        if len(images) > 0:
            logger.info('Latest image found: {}, {}'.format(images[0]['Name'], images[0]['ImageId']))
            return images[0]['ImageId']
        else:
            logger.error('Image not found.')
            raise Exception('Image not found.')
    except Exception as e:
        logger.error('Error occurred while describing images: {}'.format(e))
        raise e

def lambda_handler(event, context):
    logger.info('Received event: {}'.format(json.dumps(event)))
    response_data = {
        "Message": "No action is needed."
    }
    properties = event['ResourceProperties']

    try:
        if event['RequestType'] == 'Create':
            if event['ResourceType'] == 'Custom::CreateUuid':
                response_data = {
                    "UUID": str(uuid.uuid4())
                }
            elif event['ResourceType'] == 'Custom::GetAMIInfo':
                ami_name = properties['AMI_NAME']
                response_data = {
                    "ImageId": get_ami_info(ami_name)
                }
         
        if event['ResourceType'] == 'Custom::SendAnonymousMetric':
            solution_id = properties['SolutionId']
            solution_version = properties['SolutionVersion']
            solution_uuid = properties['SolutionUuid']
            region = properties['Region']
            send_anonymous_metric(solution_id, solution_version, solution_uuid, region, event['RequestType'])
            response_data = {
                "Message": "Sent anonymous metric"
            }

        send_response(event, context, 'SUCCESS', response_data)
    except Exception as e:
        logger.error('Error: {}'.format(e))
        response_data = {
            'Error': e
        }
        send_response(event, context, 'FAILED', response_data)
