from functools import cache

import boto3


@cache
def dynamodb_resource():
    return boto3.resource(service_name="dynamodb")
