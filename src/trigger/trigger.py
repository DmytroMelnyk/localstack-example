from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    DynamoDBStreamEvent,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

tracer = Tracer(service="dynamo-stream")


@tracer.capture_lambda_handler  # type: ignore
@event_source(data_class=DynamoDBStreamEvent)
def handler(event: DynamoDBStreamEvent, context: LambdaContext):
    for record in event.records:
        if record.dynamodb:
            print(
                f"Are records equal? {record.dynamodb.new_image == record.dynamodb.old_image}"
            )
