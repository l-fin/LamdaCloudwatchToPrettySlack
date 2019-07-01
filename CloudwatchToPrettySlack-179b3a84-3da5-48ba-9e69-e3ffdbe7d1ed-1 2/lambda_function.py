import os
import json
import logging

from botocore.vendored import requests
from slacker import Slacker
from dateutil.parser import parse
from datetime import timedelta

'''
token : OAuth access token for bot
'''

TOKEN = os.environ['token']
CHANNEL = os.environ['channel']
TIME_DIFFERENCE = os.environ['timeDifference']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def check_comparance(oper):
    if oper == 'GreaterThanThreshold':
        return 'greater than the threshold'
    elif oper == 'GreaterThanOrEqualToThreshold':
        return 'greater than or equal to the threshold'
    elif oper == 'LessThanThreshold':
        return 'less than the threshold'
    else:
        return 'less than or equal to the threshold'

def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))
    
    alarm_name = message['AlarmName']
    alarm_time = message['StateChangeTime']
    new_state = message['NewStateValue']
    trigger = message['Trigger']['MetricName']
    threshold = message['Trigger']['Threshold']

    parsed_time = (parse(alarm_time) + timedelta(hours=int(TIME_DIFFERENCE))).strftime("%Y/%m/%d %H:%M:%S")
    datapoint = ((message['NewStateReason'].split('['))[1].split())[0]
    comparance = check_comparance(message['Trigger']['ComparisonOperator'])
    reason = trigger + '(' + datapoint + ')' + (' was ' if new_state == 'ALARM' else ' was not ') + comparance + '(' + str(threshold) + ')'
    slack = Slacker(TOKEN)

    attachments_dict = dict()
    attachments_dict['color'] = 'good' if new_state == 'OK' else 'danger'
    attachments_dict['pretext'] = '*```%s```*' % alarm_name
    attachments_dict['text'] = '*State:* %s %s\n*Time:* %s\n\n*Threshold(Reason)* \n%s' % (
        ':white_check_mark:' if new_state == 'OK' else ':question:', new_state, parsed_time, reason)
    attachments_dict['mrkdwn_in'] = ["text", "pretext"]
    attachments_dict['field'] = dict()
    attachments_dict['field']['text'] = 'hello'
    attachments = [attachments_dict]
    
    slack.chat.post_message(CHANNEL, username='AWS Monitoring Bot', icon_emoji=':robot_face:', attachments=attachments)