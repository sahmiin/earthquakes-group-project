"""
Produces earthquake email alerts via AWS SNS
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from os import environ as ENV
import json

import boto3
from psycopg2 import connect, Connection

# Classes


@dataclass(frozen=True)
class Subscriber:
    subscriber_id: int
    subscriber_name: str
    subscriber_email: str
    weekly: bool
    country_id: int
    magnitude_value: float


@dataclass(frozen=True)
class EarthquakeEvent:
    earthquake_id: int
    country_id: int
    magnitude: float
    occurred_at: str
    place: str = None
    country_name: str = None


def get_boto3_client(region):
    """Returns a boto3 client"""
    return boto3.client(
        "sns", region_name=region) if region else boto3.client("sns")


def get_pg_connection() -> Connection:
    """Returns a connection to the RDS"""
    return connect(
        host=ENV["HOST_NAME"],
        port=int(ENV.get("PORT", "5432")),
        dbname=ENV["DATABASE_NAME"],
        user=ENV["DATABASE_USERNAME"],
        password=ENV["DATABASE_PASSWORD"],
        connect_timeout=5,
    )


def fetch_subscribers(conn: Connection, *, schema: str, table: str) -> list[Subscriber]:
    """Returns a list of subscribers"""
    query = f"""
        SELECT
            subscriber_id,
            subscriber_name,
            subscriber_email,
            weekly,
            country_id,
            magnitude_value
        FROM {schema}.{table}
        WHERE subscriber_email IS NOT NULL;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    subs: list[Subscriber] = []
    for r in rows:
        (
            subscriber_id,
            subscriber_name,
            subscriber_email,
            weekly,
            country_id,
            magnitude_value,
        ) = r

        subs.append(
            Subscriber(
                subscriber_id=int(subscriber_id),
                subscriber_name=str(
                    subscriber_name) if subscriber_name is not None else "",
                subscriber_email=str(subscriber_email),
                weekly=bool(weekly) if weekly is not None else None,
                country_id=int(country_id) if country_id is not None else None,
                magnitude_value=float(
                    magnitude_value) if magnitude_value is not None else None,
            )
        )

    return subs


def fetch_country_name(
    conn: Connection,
    *,
    country_id: int,
    schema: str,
    table: str,
    id_col: str = "country_id",
    name_col: str = "country_name",
) -> str:
    """Fetches country name based on matching id in alert"""
    query = f"""
        SELECT {name_col}
        FROM {schema}.{table}
        WHERE {id_col} = %s
        LIMIT 1;
    """
    with conn.cursor() as cur:
        cur.execute(query, (country_id,))
        row = cur.fetchone()

    if not row:
        return None
    return str(row[0]) if row[0] is not None else None


# Preferences
def matches(sub: Subscriber, event: EarthquakeEvent) -> bool:
    """Returns a boolean based on whether or not there is a matching preference"""
    if sub.country_id is not None and sub.country_id != event.country_id:
        return False
    if sub.magnitude_value is not None and event.magnitude < sub.magnitude_value:
        return False
    return True


# SNS filter policies
def build_filter_policy(sub: Subscriber) -> dict[str]:
    """
    Builds the SNS subscription FilterPolicy based on subscriber preferences.
    """
    policy: Dict[str, Any] = {}

    if sub.country_id is not None:
        policy["country_id"] = [str(sub.country_id)]

    if sub.magnitude_value is not None:
        policy["magnitude"] = [{"numeric": [">=", float(sub.magnitude_value)]}]

    return policy


def subscribe_with_filter_policy(
    sns,
    *,
    topic_arn: str,
    email: str,
    filter_policy: dict[str],
) -> str:
    """
    Subscribe an email endpoint and set its filter policy
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
    *,
    topic_arn: str,
    subject: str,
    body: str,
    country_id: int,
    magnitude: float,
) -> None:
    """Publishes an event to the SNS"""
    sns.publish(
        TopicArn=topic_arn,
        Subject=subject[:100],
        Message=body,
        MessageAttributes={
            "country_id": {"DataType": "String", "StringValue": str(country_id)},
            "magnitude": {"DataType": "Number", "StringValue": str(float(magnitude))},
        },
    )


# Message formatting
def format_subject(event: EarthquakeEvent) -> str:
    """Formats the subject of the alert"""
    country = event.country_name or f"country_id={event.country_id}"
    return f"Earthquake alert: M{event.magnitude:.1f} in {country}"


def format_body(event: EarthquakeEvent) -> str:
    """Formats the body of the alert"""
    country = event.country_name or f"(country_id={event.country_id})"
    place = f"\nLocation: {event.place}" if event.place else ""
    return (
        "An earthquake has been recorded.\n\n"
        f"Earthquake ID: {event.earthquake_id}\n"
        f"Time: {event.occurred_at}\n"
        f"Country: {country}\n"
        f"Magnitude: {event.magnitude}\n"
        f"{place}\n"
    )


# Service entrypoint
def handle_earthquake_alert(
    event: EarthquakeEvent,
    *,
    schema: str = "earthquakes",
    subscriber_table: str = "subscribers",
    country_table: str = "country",
    country_id_col: str = "country_id",
    country_name_col: str = "country_name",
    topic_arn: str = None,
    sns_client=get_boto3_client(ENV["AWS_REGION"]),
    subscribe_every_time: bool = True,
) -> dict[str]:
    """
    Resolves country name for nicer output
    Fetches subscribers from DB
    Publish the earthquake event ONCE (SNS routes based on filter policies)
    Returns operational counts.
    """
    if topic_arn is None:
        topic_arn = ENV.get("SNS_TOPIC_ARN")
    if not topic_arn:
        raise ValueError(
            "SNS_TOPIC_ARN env var is required (Topic ARN for c21-earthquake-alerts).")

    with get_pg_connection() as conn:
        country_name = fetch_country_name(
            conn,
            country_id=event.country_id,
            schema=schema,
            table=country_table,
            id_col=country_id_col,
            name_col=country_name_col,
        )
        event = replace(event, country_name=country_name)

        subs = fetch_subscribers(conn, schema=schema, table=subscriber_table)

    matched_count = sum(1 for s in subs if matches(s, event))

    subscribed_attempts = 0
    confirmed_subscriptions = 0
    pending_confirmations = 0
    filter_policies_set = 0

    if subscribe_every_time:
        for s in subs:
            policy = build_filter_policy(s)
            sub_arn = subscribe_with_filter_policy(
                sns_client,
                topic_arn=topic_arn,
                email=s.subscriber_email,
                filter_policy=policy,
            )
            subscribed_attempts += 1
            if sub_arn and sub_arn.lower().startswith("pending"):
                pending_confirmations += 1
            elif sub_arn:
                confirmed_subscriptions += 1
                filter_policies_set += 1

    subject = format_subject(event)
    body = format_body(event)

    publish_event_once(
        sns_client,
        topic_arn=topic_arn,
        subject=subject,
        body=body,
        country_id=event.country_id,
        magnitude=event.magnitude,
    )

    return {
        "topic_arn": topic_arn,
        "country_name": country_name,
        "matched": int(matched_count),
        "published": 1,
        "subscribed_attempts": int(subscribed_attempts),
        "confirmed_subscriptions_with_policy_set": int(confirmed_subscriptions),
        "pending_confirmations": int(pending_confirmations),
        "filter_policies_set": int(filter_policies_set),
    }


# Lambda handler
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
            schema=event.get("schema", "earthquakes"),
            subscriber_table=event.get("subscriber_table", "subscribers"),
            country_table=event.get("country_table", "country"),
            country_id_col=event.get("country_id_col", "country_id"),
            country_name_col=event.get("country_name_col", "country_name"),
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
                # operational metrics
                "matched": result.get("matched"),
                "published": result.get("published"),
                "subscribed_attempts": result.get("subscribed_attempts"),
                "pending_confirmations": result.get("pending_confirmations"),
                "filter_policies_set": result.get("filter_policies_set"),
            }
        ),
    }
