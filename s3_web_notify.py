# -*- coding: utf-8 -*-

import re
import utils

from botocore.exceptions import ClientError
from sceptre.hooks import Hook


class S3WebNotify(Hook):
    """
    Hook for notifying about provisioned resources.

    :param argument: The Sender name and email
    :type argument: str

    """
    def __init__(self, *args, **kwargs):
        super(S3WebNotify, self).__init__(*args, **kwargs)

    def run(self):
        """
        Notify resource owner of the provisioned website.
        """
        args = self.argument
        utils.validate_args(args)
        sender_name = args.split(' ')[0]
        sender_email = args.split(' ')[1]

        # Defaults parameters allows user to optionally specify them in scepter
        # Therefore we need to get parameter values from cloudformation
        connection_manager = self.stack.connection_manager
        try:
            response = connection_manager.call(
                service="cloudformation",
                command="describe_stacks",
                kwargs={"StackName": self.stack.external_name},
                profile=self.stack.profile,
                region=self.stack.region,
                stack_name=self.stack.name
            )
        except ClientError as e:
            raise e

        stack_parameters = response['Stacks'][0]['Parameters']
        stack_outputs = response['Stacks'][0]['Outputs']
        owner_email = utils.get_parameter_value(stack_parameters, 'OwnerEmail')
        website_bucket = utils.get_output_value(
            stack_outputs,
            self.stack.region + '-' + self.stack.external_name + '-' + 'WebsiteBucket')
        self.logger.info("Website bucket name: " +  website_bucket)
        cloudfront_endpoint = utils.get_output_value(
            stack_outputs,
            self.stack.region + '-' + self.stack.external_name + '-' + 'CloudfrontEndpoint')
        self.logger.info("Cloudfront endpoint: " +  cloudfront_endpoint)

        message =  ("A cloudfront website has been provisioned on your behalf."
                    " The contents of the website is in an S3 bucket. "
                    " The bucket name is " + website_bucket +
                    " The cloudfront endpoint is " + cloudfront_endpoint)
        try:
            response = utils.email_owner(
                self.stack,
                sender_email,
                owner_email,
                sender_name + " Automated Provisioner",
                message)
        except ClientError as e:
            self.logger.error(e.response['Error']['Message'])
        else:
            self.logger.info("Email sent to " + owner_email)
            self.logger.info("Message ID: " + response['MessageId'])
