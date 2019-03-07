---
layout: docs
title: Hooks
---

# Overview

These hooks are utilities for the Sage auto provisioner to run either
pre or post processing on deployment of AWS resources.


These hooks will use the AWS SES service to send email notifications.
A sender name and email is required. A good email to use is the AWS account's
root email address because it has already been verified by SES.  If you prefer
to use a different sender email address and your AWS SES is still in the
[SES sandbox](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/request-production-access.html)
then you must manually verify that email before it can be used.

## Available Hooks

### ec2_notify

Email notify the resource owner that their EC2 instance has been
provisioned and provide the necessary info to access the instance.

Syntax:

```yaml
parameter|sceptre_user_data:
    <name>: !ec2_notify <sender_name> <sender_email>
```

Example:

Email notify about the resource after creating or updating it.
```
parameters:
  OwnerEmail: "joe.smith@acme.org"
hooks:
  after_create:
    - !ec2_notify Scicomp it@acme.org
  after_update:
    - !ec2_notify Scicomp it@acme.org
```

### s3_notify

Run additional setup after creating a bucket:

* For a general bucket send an email to the bucket owner with bucket info.
* For a Synapse read-write bucket create an owner.txt file and upload it to the bucket then send notification.  
For more information please refer to the
[synapse external bucket documention](http://docs.synapse.org/articles/custom_storage_location.html)


Syntax:

```yaml
parameter|sceptre_user_data:
    <name>: !s3_notify <sender_name> <sender_email>
```

Example:

```
parameters:
  SynapseUserName: "jsmith"
  OwnerEmail: "joe.smith@acme.org"
hooks:
  after_create:
    - !s3_notify Scicomp it@acme.org
```

### s3_web_notify

Email notify the resource owner that their S3 website has been
provisioned and provide the info to access the website.

Syntax:

```yaml
parameter|sceptre_user_data:
    <name>: !s3_web_notify <sender_name> <sender_email>
```

Example:

```
parameters:
  OwnerEmail: "joe.smith@acme.org"
hooks:
  after_create:
    - !s3_web_notify Scicomp it@acme.org
```


## Deprecated Hooks
These hooks are not supported anymore.

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
```

