"""Handles connection to SNS subscription group, builds filters"""
import json

import boto3


def get_sns_client(region: str):
    """Returns a boto3 SNS client."""
    return boto3.client("sns", region_name=region) if region else boto3.client("sns")


def build_filter_policy(country_id: int, magnitude_value: float) -> dict[str: int | float]:
    """
    Builds the SNS subscription FilterPolicy based on subscriber preferences.
    """
    policy: dict[str: int | float] = {}

    if country_id is not None:
        policy["country_id"] = [str(country_id)]

    if magnitude_value is not None:
        policy["magnitude"] = [{"numeric": [">=", float(magnitude_value)]}]

    return policy


def list_topic_subscriptions_map(sns, topic_arn: str) -> dict[str: str]:
    """
    Returns mapping: email endpoint -> SubscriptionArn for the given topic.
    """
    mapping: dict[str: str] = {}
    token: str = None

    while True:
        kwargs = {"TopicArn": topic_arn}
        if token:
            kwargs["NextToken"] = token

        resp = sns.list_subscriptions_by_topic(**kwargs)

        for sub in resp.get("Subscriptions", []):
            endpoint = sub.get("Endpoint")
            arn = sub.get("SubscriptionArn")
            if endpoint and arn:
                mapping[str(endpoint)] = str(arn)

        token = resp.get("NextToken")
        if not token:
            break

    return mapping


def ensure_email_subscription_with_policy(
    sns,
    topic_arn: str,
    email: str,
    filter_policy: dict[str: int | float],
    existing_map: dict[str: str],
) -> str:
    """
    If the email is already subscribed to the topic, do not subscribe again.
    If confirmed, update FilterPolicy. If pending, skip policy update.
    If not subscribed, subscribe (will send confirmation).
    """
    sub_arn = existing_map.get(email)

    if sub_arn:
        # Already subscribed: avoid duplicate subscribe requests/confirmation emails
        if not sub_arn.lower().startswith("pending"):
            sns.set_subscription_attributes(
                SubscriptionArn=sub_arn,
                AttributeName="FilterPolicy",
                AttributeValue=json.dumps(filter_policy),
            )
        return sub_arn

    # Not subscribed yet -> subscribe
    resp = sns.subscribe(
        TopicArn=topic_arn,
        Protocol="email",
        Endpoint=email,
        ReturnSubscriptionArn=True,
    )
    return resp.get("SubscriptionArn", "")


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
