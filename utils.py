# -*- coding: utf-8 -*-

import re

from botocore.exceptions import ClientError
from exceptions import UndefinedExportException, UndefinedParameterException
from constants import EMAIL_REGEX

def validate_args(argument):
    # get sceptre arguments sender name and email
    args = argument
    if not args or ' ' not in args or len(args.split(' ')) != 2:
        raise ValueError("Invalid arguments, args must be: "
                         "<sender_name> <sender_email>")
    sender_name = args.split(' ')[0]
    sender_email = args.split(' ')[1]
    if re.match(EMAIL_REGEX, sender_email) == None:
        raise ValueError("Invalid sender email: %s", sender_email)

def get_parameter_value(parameters, key):
    for parameter in parameters:
        if parameter['ParameterKey'] == key:
            return parameter['ParameterValue']

    raise UndefinedParameterException("Parameter not found: " + key)

def get_output_value(exports, name):
    for export in exports:
        if export['ExportName'] == name:
            return export['OutputValue']

    raise UndefinedExportException("Export not found: " + name)

def email_owner(stack, sender, recipient, subject, body):

    BODY_TEXT = body

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

    client = stack.template.connection_manager
    try:
        # Provide the contents of the email.
        response = client.call(
            service="ses",
            command="send_email",
            profile=stack.profile,
            region=stack.region,
            stack_name=stack.name,
            kwargs={
                "Source": sender,
                "Destination": {
                    "ToAddresses": [
                        recipient
                    ],
                },
                "Message": {
                    "Body": {
                        "Html": {
                            "Charset": CHARSET,
                            "Data": BODY_HTML1 + BODY_TEXT + BODY_HTML2,
                        },
                        "Text": {
                            "Charset": CHARSET,
                            "Data": BODY_TEXT,
                        },
                    },
                    "Subject": {
                        "Charset": CHARSET,
                        "Data": subject,
                    },
                },
            }
        )
    except ClientError as e:
        raise e
    else:
        return response
