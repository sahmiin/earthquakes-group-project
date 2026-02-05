"""Lambda function entrypoint"""
from __future__ import annotations

from os import environ as ENV
import json

from .classes import EarthquakeEvent
from .sns_client import get_sns_client
from .service import handle_earthquake_alert


SNS = get_sns_client(ENV.get("AWS_REGION"))


def lambda_handler(event, context):
    """
    Lambda entrypoint
    """
    event = event or {}

    missing = [k for k in ("earthquake_id", "country_id",
                           "magnitude", "occurred_at") if k not in event]
    if missing:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing required fields.", "missing": missing}),
        }

    eq = EarthquakeEvent(
        earthquake_id=int(event["earthquake_id"]),
        country_id=int(event["country_id"]),
        magnitude=float(event["magnitude"]),
        occurred_at=str(event["occurred_at"]),
        place=event.get("place"),
    )

    try:
        result = handle_earthquake_alert(
            eq,
            sns_client=SNS,
            topic_arn=event.get("topic_arn"),
            subscribe_every_time=bool(event.get("subscribe_every_time", True)),
        )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal error processing alert.", "error": str(e)}),
        }

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Processed earthquake notification event.",
                "earthquake_id": eq.earthquake_id,
                "country_id": eq.country_id,
                "country_name": result.get("country_name"),
                "magnitude": eq.magnitude,
                "topic_arn": result.get("topic_arn"),
                "matched": result.get("matched"),
                "published": result.get("published"),
                "subscribed_attempts": result.get("subscribed_attempts"),
                "pending_confirmations": result.get("pending_confirmations"),
                "filter_policies_set": result.get("filter_policies_set"),
            }
        ),
    }
