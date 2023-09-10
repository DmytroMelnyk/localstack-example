import time

from .common import dynamodb_resource


def hello(table, event, logger) -> float:
    tic = time.perf_counter()
    res = dynamodb_resource()
    toc = time.perf_counter()
    try:
        table.update_item(
            Key={"path": event.path},
            UpdateExpression="ADD hits :incr",
            ExpressionAttributeValues={":incr": 1},
        )
    except res.meta.client.exceptions.ConditionalCheckFailedException:
        logger.error("trouble")

    return tic - toc
