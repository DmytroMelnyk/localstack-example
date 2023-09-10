from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.api_gateway_proxy_event import (
    APIGatewayProxyEvent,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

from .domain import BarModel, FooModel, ParentModel, UserModel

tracer = Tracer(service="api-handler")

UserModel.create_table(wait=True, billing_mode="PAY_PER_REQUEST")
ParentModel.create_table(wait=True, billing_mode="PAY_PER_REQUEST")


@tracer.capture_lambda_handler  # type: ignore
@event_source(data_class=APIGatewayProxyEvent)
def handler(event: APIGatewayProxyEvent, context: LambdaContext):
    user = UserModel("John", "Denver")
    user.email = "djohn@company.org"
    user.save()

    foo = FooModel("1", "range")
    foo.foo = "foo"
    foo.save()
    bar = BarModel("2", "range")
    bar.bar = "bar"
    bar.save()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": user.to_json(),
    }
