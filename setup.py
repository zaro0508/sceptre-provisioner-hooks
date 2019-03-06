#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

with open("README.md") as readme_file:
    readme = readme_file.read()

install_requirements = [
    "sceptre>=2.0"
]

setup(
    name='sceptre-provisioner-hooks',
    version="1.0.0",
    description="Sceptre hooks to help facilitate the"
                "Sage auto provisioner",
    py_modules=['ec2_notify',
                's3_notify',
                'synapse_bucket_notify',
                's3_web_notify',
                'utils',
                'constants',
                'exceptions',],
    long_description=readme,
    long_description_content_type="text/markdown",
    author="zaro0508",
    author_email="zaro0508@gmail.com",
    license='Apache2',
    url="https://github.com/Sage-Bionetworks/sceptre-provisioner-hooks",
    entry_points={
        'sceptre.hooks': [
            'ec2_notify = '
            'ec2_notify:EC2Notify',
            's3_notify = '
            's3_notify:S3Notify',
            'synapse_bucket_notify = '
            'synapse_bucket_notify:SynapseBucketNotify',
            's3_web_notify = '
            's3_web_notify:S3WebNotify',
        ],
    },
    keywords="sceptre",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Environment :: Console",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],
    install_requires=install_requirements,
    include_package_data=True,
    zip_safe=False,
)
