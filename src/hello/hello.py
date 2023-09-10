import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import (
    event_source,
)
from aws_lambda_powertools.utilities.data_classes.api_gateway_proxy_event import (
    APIGatewayProxyEvent,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

from .common import dynamodb_resource
from .func_usage import hello

ddb = dynamodb_resource()
table = ddb.Table(os.environ["HITS_TABLE_NAME"])
tracer = Tracer(service="hello-handler")
logger = Logger(service="hello-handler")


@tracer.capture_lambda_handler  # type: ignore
@event_source(data_class=APIGatewayProxyEvent)
def handler(event: APIGatewayProxyEvent, context: LambdaContext):
    tictoc = hello(table, event, logger)

    logger.info(event.path)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": f"Hello from lambda! Path is: '{event.path}'. ResInitTime: {tictoc:0.4f} seconds",
    }


# handler(
#     APIGatewayProxyEvent({"rawPath": "/", "requestContext": {"stage": "$default"}}),
#     None,
# )
