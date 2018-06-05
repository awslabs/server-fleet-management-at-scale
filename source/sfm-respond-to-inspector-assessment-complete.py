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
import boto3
import json
import os
import urllib
from datetime import datetime
from urllib import request
from urllib import parse

INSPECTOR_RESOURCE_LIMIT = 500
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create the clients outside of the handler.
inspector_client = boto3.client('inspector')
sns_client = boto3.client('sns')

#==================================================
# Default handler
#
# Inputs:
#     - SNS message payload that includes assessment run ARN
#
# Outputs:
#     - AssessmentRunArn
#     - AgentId
#==================================================
def lambda_handler(event, context):

    logger.info('Event: {}'.format(json.dumps(event)))

    # First, get the Inspector assessment run ARN from the event.
    assessment_run_arn = json.loads(event['Records'][0]['Sns']['Message'])['run']

    # At the time this function was written, some Inspector APIs do not
    # support pagination, so the most number of results we can get at one
    # time is 500.

    # Get the agents (instances) that participated in the assessment. We'll loop
    # through them to retrieve the findings for each agent.
    logger.debug('assessment_run_arn: {}'.format(assessment_run_arn))
    logger.debug('maxResults: {}'.format(INSPECTOR_RESOURCE_LIMIT))

    assessment_run_agents = inspector_client.list_assessment_run_agents(
        assessmentRunArn = assessment_run_arn,
        maxResults = INSPECTOR_RESOURCE_LIMIT
    )['assessmentRunAgents']

    logger.info('got {} assessment run agents.'.format(len(assessment_run_agents)))
    # Send anonymous data
    if os.environ['send_anonymous_data'].lower() == 'yes':
        logger.info('Sending anonymous metrics')
        try:
            params = {'Solution': 'SO0043',
                'UUID': os.environ['uuid'],
                'Data': {'ManagedInstanceCount': len(assessment_run_agents)},
                'TimeStamp': str(datetime.utcnow().isoformat())
            }
            logger.debug('Anonymous data: {}'.format(json.dumps(params)))
            url = 'https://metrics.awssolutionsbuilder.com/generic'
            data = parse.urlencode(params).encode('ascii')
            headers = {'Content-Type':'application/json'}

            req = request.Request(url, data, headers)
            resp =  request.urlopen(req)
            logger.info('Anonymous Metrics Response Code: {}'.format(resp.getcode()))

        except Exception as e:
            logger.error("Exception sending anonymous metrics: {}".format(e))
    # End send anonymous data

    for assessment_run_agent in assessment_run_agents:

        logger.debug('topic arn: {}'.format(os.environ['assessment_agent_id_notification_topic_arn']))
        logger.debug('assessment run arn: {}'.format(assessment_run_arn))
        logger.debug('agent id: {}'.format(assessment_run_agent['agentId']))

        # Post to SNS topic. A Lambda function that listens for these notifications
        # will be executed for each agent in this loop.
        sns_client.publish(
            TopicArn = os.environ['assessment_agent_id_notification_topic_arn'],
            Message = json.dumps(
                {
                    "AssessmentRunArn": assessment_run_arn,
                    "AgentId": assessment_run_agent['agentId']
                }
            )
        )

    return
