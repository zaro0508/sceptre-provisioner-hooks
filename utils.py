# -*- coding: utf-8 -*-

from botocore.exceptions import ClientError
from exceptions import UndefinedExportException, UndefinedParameterException

def get_parameter_value(self, parameters, key):
    for parameter in parameters:
        if parameter['ParameterKey'] == key:
            return parameter['ParameterValue']

    raise UndefinedParameterException("Parameter not found: " + key)


def get_output_value(self, exports, name):
    for export in exports:
        if export['ExportName'] == name:
            return export['OutputValue']

    raise UndefinedExportException("Export not found: " + name)


def email_owner(self, sender, recipient, message):
    client = self.connection_manager.boto_session.client('ses')

    SENDER_NAME = sender['SenderName']

    # This address must be verified with Amazon SES.
    SENDER_EMAIL = sender['SenderEmail']

    # if SES is still in the sandbox, this address must be verified.
    RECIPIENT = recipient

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    # AWS_REGION = "us-west-2"

    # The subject line for the email.
    SUBJECT = SENDER_NAME + " Automated Provisioning"

    BODY_TEXT = message

    # The HTML body of the email.
    BODY_HTML1 = """<html>
    <head></head>
    <body>
      <p>"""
    BODY_HTML2 = """</p>
    </body>
    </html>
    """

    # The character encoding for the email.
    CHARSET = "UTF-8"

    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML1 + BODY_TEXT + BODY_HTML2,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER_EMAIL,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        self.logger.error(e.response['Error']['Message'])
    else:
        self.logger.info("Email sent to " + RECIPIENT)
        self.logger.info("Message ID: " + response['MessageId'])
