"""Lambda Function Handler script"""
import json
from os import environ as ENV

from sns_client import get_sns_client
from db_queries import get_pg_connection
from poll_service import handle_recent_earthquakes

SNS = get_sns_client(ENV.get("AWS_REGION"))


def lambda_handler(event, context):
    """
    Lambda Entrypoint
    """
    event = event or {}

    topic_arn = ENV.get("SNS_TOPIC_ARN")
    if not topic_arn:
        return {"statusCode": 500, "body": json.dumps({"message": "SNS_TOPIC_ARN not set"})}

    subscribe_every_time = bool(event.get("subscribe_every_time", True))

    try:
        with get_pg_connection() as conn:
            result = handle_recent_earthquakes(
                conn,
                sns_client=SNS,
                topic_arn=topic_arn,
                subscribe_every_time=subscribe_every_time,
            )
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": "Internal error", "error": str(e)})}

    return {"statusCode": 200, "body": json.dumps(result)}
