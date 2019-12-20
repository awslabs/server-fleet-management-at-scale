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
import boto3
import json
import datetime
import operator
import botocore

FINDING_SORT_ORDER = {"High":"1", "Medium":"2", "Low":"3", "Informational":"4"}
INSPECTOR_RESOURCE_LIMIT = 500
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create the clients outside of the handler.
inspector_client = boto3.client('inspector')
ssm_client = boto3.client('ssm')

#==================================================
# Default handler
#
# Inputs:
#     - AssessmentRunArn
#     - AgentId
#==================================================
def lambda_handler(event, context):

    logger.info('Event: {}'.format(json.dumps(event)))

    now = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"

    assessment_run_arn = json.loads(event['Records'][0]['Sns']['Message'])['AssessmentRunArn']
    instance_id = json.loads(event['Records'][0]['Sns']['Message'])['AgentId']

    # Get the list of findings for the given agent on the given assessment run.
    findings_arns = inspector_client.list_findings(
        assessmentRunArns = [assessment_run_arn],
        filter={'agentIds': [instance_id]},
        maxResults = INSPECTOR_RESOURCE_LIMIT
    )['findingArns']

    logger.info('AssessmentRunArn: {}, AgentId: {}, FindingsArn: {}'.format(assessment_run_arn,instance_id,findings_arns))

    # Now get the findings details.
    if findings_arns:
        logger.info('getting the findings details')
        ssm_findings = []
        findings = inspector_client.describe_findings(findingArns = findings_arns)['findings']

        inventories = {}

        # Loop through the findings.
        logger.info('looping through the findings')
        for finding in findings:

            inventory_finding = {
                "Finding":finding['id'],
                "Severity":finding['severity'],
                "Criticality":FINDING_SORT_ORDER[finding['severity']]
            }
            logger.debug('inventory finding: {}'.format(inventory_finding))

            # Build the JSON object that we can use for the SSM inventory.
            ssm_findings.append(inventory_finding)

            inventories[instance_id] = ssm_findings

            # Sort the findings by their severity (defined by their sort value).
            for instance in inventories:
                inventories[instance].sort(key=operator.itemgetter('Criticality'))

            # Lastly, for each instance, report the inventory of findings.
            for instance_id, content in inventories.items():

                # The instance may have terminated since the assessment was run, so we
                # need to account for API failures.
                try:
                    ssm_client.put_inventory(
                        InstanceId = instance_id,
                        Items = [
                            {
                                "CaptureTime": now,
                                "SchemaVersion": "1.1",
                                "TypeName": "Custom:InspectorFindings",
                                "Content": content
                            }
                        ]
                    )

                except botocore.exceptions.ClientError as e:
                    logger.error('Error putting inventory to instance {0}: {1}'.format(instance_id, e))

    return
