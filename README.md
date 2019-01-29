---
layout: docs
title: Hooks
---

# Overview

These hooks are utilities for the Sage auto provisioner to run either
pre or post processing on deployment of AWS resources.


Notifications hooks will use the AWS SES service. A sender name and email
is required to send notifications. A good email to use is the AWS account's
root email address because it has already been verified by SES.  If you prefer
to use a different email address and your AWS SES is still in the
[SES sandbox](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/request-production-access.html)
you must manually verify the sender email before it can be used. 

## Available Hooks

### ec2_notify

Email notify the resource owner that their EC2 instance has been
provisioned and provide info to access the instance.

Syntax:

```yaml
parameter|sceptre_user_data:
    <name>: !ec2_notification <sender_name> <sender_email>
```

Example:

Email notify about the resource after creating or updating it.
```
parameters:
  OwnerEmail: "joe.smith@acme.org"
hooks:
  after_create:
    - !ec2_notification Scicomp it@acme.org
  after_update:
    - !ec2_notification Scicomp it@acme.org
```

### synapse_bucket_notify

Run additional setup after creating a Synapse external bucket.
For more information please refer to the
[synapse external bucket documention](http://docs.synapse.org/articles/custom_storage_location.html)

Does the following after creation of the bucket:
* Upload an owner.txt file to the bucket.
* Send an email to the bucket owner with the bucket info.

Syntax:

```yaml
parameter|sceptre_user_data:
    <name>: !synapse_bucket_notify <sender_name> <sender_email>
```

Example:

```
parameters:
  SynapseUserName: "jsmith"
  OwnerEmail: "joe.smith@acme.org"
hooks:
  after_create:
    - !synapse_bucket_notify Scicomp it@acme.org
  after_update:
    - !synapse_bucket_notify Scicomp it@acme.org
```

### s3_web_notify

Email notify the resource owner that their S3 website has been
provisioned and provide info to access the website.

Syntax:

```yaml
parameter|sceptre_user_data:
    <name>: !synapse_bucket_notify <sender_name> <sender_email>
```

Example:

```
parameters:
  SynapseUserName: "jsmith"
  OwnerEmail: "joe.smith@acme.org"
hooks:
  after_create:
    - !synapse_bucket_notify Scicomp it@acme.org
  after_update:
    - !synapse_bucket_notify Scicomp it@acme.org
```
