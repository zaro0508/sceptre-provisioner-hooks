# -*- coding: utf-8 -*-

import utils

from botocore.exceptions import ClientError
from sceptre.hooks import Hook
from exceptions import UndefinedParameterException


class S3Notify(Hook):
    """
    Hook for notifying about provisioned resources.

    :param argument: The Sender name and email
    :type argument: str

    """
    def __init__(self, *args, **kwargs):
        super(S3Notify, self).__init__(*args, **kwargs)

    def run(self):
        """
        Notify resource owner of the provisioned bucket.
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

        # handle optional parameters
        try:
            allow_write_bucket = utils.get_parameter_value(stack_parameters, 'AllowWriteBucket')
        except UndefinedParameterException as e:
            allow_write_bucket = "false"

        try:
            synapse_username = utils.get_parameter_value(stack_parameters, 'SynapseUserName')
            if synapse_username:
                self.logger.info("synapse user name: " + synapse_username)
        except UndefinedParameterException as e:
            synapse_username = ""

        # Setup for a synapse bucket
        # Bucket name is auto generated and only available in CF outputs
        s3_bucket = utils.get_output_value(
            stack_outputs,
            self.stack.region + '-' + self.stack.external_name + '-' + 'SynapseExternalBucket')
        self.logger.info("bucket name: " +  s3_bucket)
        if allow_write_bucket.lower() == 'true' and synapse_username:
            self.create_owner_file(synapse_username, s3_bucket)

        # Send notification to resource owner
        message =  ("A S3 bucket has been provisioned on your behalf.\n"
                    " Cloudformation stack: " + self.stack.name + "\n"
                    " Bucket name: " + s3_bucket + "\n")
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

    def create_owner_file(self, synapse_username, s3_bucket):
        connection_manager = self.stack.connection_manager
        OWNER_FILE = 'owner.txt'
        try:
            response = connection_manager.call(
                service="s3",
                command="put_object",
                kwargs={"Body": synapse_username.encode('UTF-8'),
                        "Bucket": s3_bucket,
                        "Key": OWNER_FILE
                        },
                profile=self.stack.profile,
                region=self.stack.region,
                stack_name=self.stack.name
            )
        except ClientError as e:
            self.logger.error(e.response['Error']['Message'])
            raise e
        else:
            self.logger.info("Created " + s3_bucket + "/" + OWNER_FILE),
