---
layout: docs
title: Hooks
---

# Overview

These hooks are utilities for the Sage auto provisioner to run either
pre or post processing on deployment of AWS resources.


## Available Hooks

### ec2_notify

Email notify the resource owner that their EC2 instance has been
provisioned and provide info to access the instance.

__Note__ - If your AWS SES is in the sandbox the sender email
must be verified before it can be used.

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

__Note__ - If your AWS SES is in the
[sandbox](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/request-production-access.html)
the sender email must be verified before it can be used.

Syntax:

```yaml
parameter|sceptre_user_data:
    <name>: !synapse_bucket_notify <sender_name> <sender_email>
```

Example:

```
parameters:
  SynapseUserName: "jsmith"
  OwnerEmail: "jsmith@acme.org"
hooks:
  after_create:
    - !synapse_bucket_notify Scicomp it@acme.org
  after_update:
    - !synapse_bucket_notify Scicomp it@acme.org
```
