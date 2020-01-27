'''
This is a sample Lambda function that sends an email on click of a
button. It requires these SES permissions.
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ses:GetIdentityVerificationAttributes",
                "ses:SendEmail",
                "ses:VerifyEmailIdentity"
            ],
            "Resource": "*"
        }
    ]
}


SES is available in the following AWS IoT 1-Click regions:
- US East (N. Virginia)
- US West (Oregon)
- EU (Ireland)

The following JSON template shows what is sent as the payload:
{
    "deviceInfo": {
        "deviceId": "GXXXXXXXXXXXXXXX",
        "type": "button",
        "remainingLife": 98.7,
        "attributes": {
            "projectName": "Sample-Project",
            "projectRegion": "us-west-2",
            "placementName": "Room-1",
            "deviceTemplateName": "lightButton"
        }
    },
    "deviceEvent": {
        "buttonClicked": {
            "clickType": "SINGLE",
            "reportedTime": 1521159287205
        }
    },
    "placementInfo": {
        "projectName": "Sample-Project",
        "placementName": "Room-1",
        "attributes": {
            "key1": "value1"
        },
        "devices": {
            "lightButton":"GXXXXXXXXXXXXXXX"
        }
    }
}
A "LONG" clickType is sent if the first press lasts longer than 1.5 seconds.
"SINGLE" and "DOUBLE" clickType payloads are sent for short clicks.
For more documentation, follow the link below.
http://docs.aws.amazon.com/iot/latest/developerguide/iot-lambda-rule.html
'''
from __future__ import print_function
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ses = boto3.client('ses')

# Check whether email is verified. Only verified emails are allowed to send emails to or from.
def check_email(email):
    result = ses.get_identity_verification_attributes(Identities=[email])
    attr = result['VerificationAttributes']
    if (email not in attr or attr[email]['VerificationStatus'] != 'Success'):
        logging.info('Verification email sent. Please verify it.')
        ses.verify_email_identity(EmailAddress=email)
        return False
    return True

def lambda_handler(event, context):
    logging.info('Received event: ' + json.dumps(event))
    attributes = event['placementInfo']['attributes']
    from_address = attributes['email']
    to_address = attributes['email']
    body = attributes['body']
    subject = attributes['subject']

    if not check_email(from_address):
        logging.error('From email is not verified')
        return

    if not check_email(to_address):
        logging.error('To email is not verified')
        return

    for key in attributes.keys():
        body = body.replace('{{%s}}' % (key), attributes[key])
    body = body.replace('{{*}}', json.dumps(attributes))

    dsn = event['deviceInfo']['deviceId']
    click_type = event['deviceEvent']['buttonClicked']['clickType']
    body += '\n(DSN: {}, {})'.format(dsn, click_type)
    '''body += '\n(Dear Insert_Target,)'.format(dsn, click_type)
    body += '\n'.format(dsn, click_type)
    ody += '\n(Here is the EmailBody)'.format(dsn, click_type)
    body += '\n'.format(dsn, click_type)
    body += '\n(Thanks,)'.format(dsn, click_type)
    body += '\n'.format(dsn, click_type)
    body += '\n(Signature)'.format(dsn, click_type)
    body += '\n(Insert_Target)'.format(dsn, click_type)'''
    ses.send_email(Source=from_address,
                   Destination={'Insert_TargetEmaill': [to_address]},
                   Message={'Subject': {'***Insert_Subject': subject}, 'Body': {'Text': {'Data': body}}})

    logger.info('Email has been sent')
