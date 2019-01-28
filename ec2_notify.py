# -*- coding: utf-8 -*-

import logging
import re

from botocore.exceptions import ClientError
from sceptre.hooks import Hook
from exceptions import UndefinedExportException, UndefinedParameterException
from utils import get_parameter_value, get_output_value, email_owner

class EC2Notify(Hook):
    """
    Hook for notifying about provisioned resources.

    :param argument: The Sender name and email
    :type argument: str

    """
    EMAIL_REGEX = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        super(EC2Notify, self).__init__(*args, **kwargs)

    def run(self):
        """
        Notify resource owner of the provisioned EC2.
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
        owner_email = get_parameter_value(stack_parameters, 'OwnerEmail')

        # EC2 info is auto assigned and only available in CF outputs
        ec2_info ={}
        ec2_info['id'] = get_output_value(
            stack_outputs, region + '-' + stack_name + '-' + 'Ec2InstanceId')
        ec2_info['private_ip'] = get_output_value(
            stack_outputs, region + '-' + stack_name + '-' + 'Ec2InstancePrivateIp')

        # EC2 in private subnet will not have a pubilc IP
        try:
            ec2_info['public_ip'] = get_output_value(
                stack_outputs, region + '-' + stack_name + '-' + 'Ec2InstancePublicIp')
        except UndefinedExportException as e:
            pass

        self.logger.info("EC2 instance id: " +  ec2_info['id'])

        info = ''
        for k, v in ec2_info.items():
            info = info + k + ": " + v + "<br />"

        message = ("An EC2 instance has been provisioned on your behalf. "
                     "<br />" + info + "<br />")
        if 'public_ip' in ec2_info:
            message = message + ("To connect to this resource, open a terminal, then type "
                                 "ssh YOUR_JUMPCLOUD_USERNAME@IP_ADDRESS@IP_ADDRESS "
                                 "(i.e. ssh jsmith@" + ec2_info["public_ip"] + ")")
        else:
            message = message + ("To connect to this resource, login to the Sage VPN, "
                                 "open a terminal, then type "
                                 "ssh YOUR_JUMPCLOUD_USERNAME@IP_ADDRESS "
                                 "(i.e. ssh jsmith@" + ec2_info["private_ip"] + ")")

        email_owner(sender, owner_email, message)
