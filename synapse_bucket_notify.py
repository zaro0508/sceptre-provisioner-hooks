# -*- coding: utf-8 -*-

import logging
import re

from botocore.exceptions import ClientError
from sceptre.hooks import Hook
from utils import get_parameter_value, get_output_value, email_owner

class SynapseBucketNotify(Hook):
    """
    Hook for notifying about provisioned resources.

    :param argument: The Sender name and email
    :type argument: str

    """
    EMAIL_REGEX = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        super(SynapseBucketNotify, self).__init__(*args, **kwargs)

    def run(self):
        """
        Notify resource owner of the provisioned bucket.
        """
        if not self.argument:
            raise ValueError("Hook requires email sender info")

        # get sceptre arguments sender name and email
        args = self.argument
        if len(args.split(' ')) != 2:
            raise ValueError("Valid arguments are <sender_name> and <sender_email>")
        sender_name = args.split(' ')[0]
        sender_email = args.split(' ')[1]
        # validate email syntax
        if re.match(self.EMAIL_REGEX, sender_email) == None:
            raise ValueError("Invalid email: %s", sender_email)

        sender = {
            "sender_name": sender_name,
            "sender_email": sender_email}
        region = self.stack.region
        stack_name = self.stack.external_name

        # Defaults parameters allows user to optionally specify them in scepter
        # Therefore we need to get parameter values from cloudformation
        connection_manager = self.stack.template.connection_manager
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
        synapse_username = get_parameter_value(stack_parameters, 'SynapseUserName')
        allow_write_bucket = get_parameter_value(stack_parameters, 'AllowWriteBucket')
        owner_email = get_parameter_value(stack_parameters, 'OwnerEmail')
        # Bucket name is auto generated and only available in CF outputs
        synapse_bucket = get_output_value(
            stack_outputs, region + '-' + stack_name + '-' + 'SynapseExternalBucket')
        self.logger.info("Synapse external bucket name: " +  synapse_bucket)

        if allow_write_bucket.lower() == 'true':
            self.create_owner_file(synapse_username, synapse_bucket)

        message =  ("An S3 bucket has been provisioned on your behalf. "
                    "The bucket name is " + synapse_bucket)
        email_owner(sender, owner_email, message)


    def create_owner_file(self, synapse_username, synapse_bucket):
        client = self.connection_manager.boto_session.client('s3')
        filename = 'owner.txt'
        try:
            client.put_object(Body=synapse_username.encode('UTF-8'),
                              Bucket=synapse_bucket,
                              Key=filename)
        except ClientError as e:
            self.logger.error(e.response['Error']['Message'])
        else:
            self.logger.info("Created " + synapse_bucket + "/" + filename),
