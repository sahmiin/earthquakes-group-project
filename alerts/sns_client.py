"""Python script containing the filter building, subscription process and event publishing"""
from __future__ import annotations

import json

import boto3


def get_sns_client(region: str):
    """Returns a boto3 SNS client."""
    return boto3.client("sns", region_name=region) if region else boto3.client("sns")


def build_filter_policy(country_id: int, magnitude_value: float) -> dict[str, int | float]:
    """
    Builds the SNS subscription FilterPolicy based on subscriber preferences.
    """
    policy: dict[str, int | float] = {}

    if country_id is not None:
        policy["country_id"] = [str(country_id)]

    if magnitude_value is not None:
        policy["magnitude"] = [{"numeric": [">=", float(magnitude_value)]}]

    return policy


def subscribe_with_filter_policy(
    sns,
    topic_arn: str,
    email: str,
    filter_policy: dict[str, int | float],
) -> str:
    """
    Subscribe an email endpoint and set its filter policy if immediately possible.

    Returns SubscriptionArn or "PendingConfirmation".
    """
    resp = sns.subscribe(
        TopicArn=topic_arn,
        Protocol="email",
        Endpoint=email,
        ReturnSubscriptionArn=True,
    )
    sub_arn = resp.get("SubscriptionArn", "")

    if sub_arn and not sub_arn.lower().startswith("pending"):
        sns.set_subscription_attributes(
            SubscriptionArn=sub_arn,
            AttributeName="FilterPolicy",
            AttributeValue=json.dumps(filter_policy),
        )

    return sub_arn


def publish_event_once(
    sns,
    topic_arn: str,
    subject: str,
    body: str,
    country_id: int,
    magnitude: float,
) -> None:
    """Publishes an event to the SNS based on preferences"""
    sns.publish(
        TopicArn=topic_arn,
        Subject=subject[:100],
        Message=body,
        MessageAttributes={
            "country_id": {"DataType": "String", "StringValue": str(country_id)},
            "magnitude": {"DataType": "Number", "StringValue": str(float(magnitude))},
        },
    )
