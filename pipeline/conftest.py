"""
AWS Lambda-ready: Immediate earthquake email alerts via AWS SNS (email protocol) + PostgreSQL.

Design:
- PostgreSQL stores subscribers and their preferences.
- Preference semantics:
    * country_id NULL => any country
    * magnitude_value NULL => any magnitude
    * otherwise notify if event.magnitude >= magnitude_value
    * AND logic when both are present
- SNS constraint:
    * SNS "email" delivers to confirmed subscriptions on a topic.
    * To email an individual subscriber, we use one topic per subscriber and store
      the topic ARN in the DB column: sns_topic_arn.

Recommended DB migration:
  ALTER TABLE alpha.subscribers
    ADD COLUMN IF NOT EXISTS sns_topic_arn TEXT;

Lambda notes:
- Do NOT call load_dotenv() in Lambda (it is harmless but unnecessary); env vars come from Lambda config.
- Create AWS clients outside the handler for connection reuse.
- Use a short DB connection per invocation (safe and typical in Lambda).
"""

from __future__ import annotations

from dataclasses import dataclass
from os import environ as ENV
from typing import Optional, List, Dict, Any
import json
import re

import boto3
import psycopg


# -------------------------
# Domain models
# -------------------------

@dataclass(frozen=True)
class Subscriber:
    subscriber_id: int
    subscriber_name: str
    subscriber_email: str
    weekly: Optional[bool]
    country_id: Optional[int]
    magnitude_value: Optional[float]
    sns_topic_arn: Optional[str]


@dataclass(frozen=True)
class EarthquakeEvent:
    earthquake_id: int
    country_id: int
    magnitude: float
    occurred_at: str
    place: Optional[str] = None


# -------------------------
# Clients (created once per warm container)
# -------------------------

_AWS_REGION = ENV.get("AWS_REGION")
_SNS = boto3.client(
    "sns", region_name=_AWS_REGION) if _AWS_REGION else boto3.client("sns")


# -------------------------
# PostgreSQL
# -------------------------

def get_pg_connection() -> psycopg.Connection:
    """
    Uses standard Postgres env vars:
      PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
    """
    return psycopg.connect(
        host=ENV["PGHOST"],
        port=int(ENV.get("PGPORT", "5432")),
        dbname=ENV["PGDATABASE"],
        user=ENV["PGUSER"],
        password=ENV["PGPASSWORD"],
        connect_timeout=5,
    )


def fetch_subscribers(conn: psycopg.Connection, *, schema: str, table: str) -> List[Subscriber]:
    query = f"""
        SELECT
            subscriber_id,
            subscriber_name,
            subscriber_email,
            weekly,
            country_id,
            magnitude_value,
            sns_topic_arn
        FROM {schema}.{table}
        WHERE subscriber_email IS NOT NULL;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    subs: List[Subscriber] = []
    for r in rows:
        (
            subscriber_id,
            subscriber_name,
            subscriber_email,
            weekly,
            country_id,
            magnitude_value,
            sns_topic_arn,
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
                sns_topic_arn=str(
                    sns_topic_arn) if sns_topic_arn is not None else None,
            )
        )

    return subs


def update_subscriber_topic_arn(
    conn: psycopg.Connection,
    *,
    schema: str,
    table: str,
    subscriber_id: int,
    topic_arn: str,
) -> None:
    query = f"""
        UPDATE {schema}.{table}
        SET sns_topic_arn = %s
        WHERE subscriber_id = %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (topic_arn, subscriber_id))
    conn.commit()


# -------------------------
# Matching logic (pure)
# -------------------------

def matches(sub: Subscriber, event: EarthquakeEvent) -> bool:
    if sub.country_id is not None and sub.country_id != event.country_id:
        return False
    if sub.magnitude_value is not None and event.magnitude < sub.magnitude_value:
        return False
    return True


# -------------------------
# SNS topic per subscriber
# -------------------------

def _safe_topic_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^A-Za-z0-9_-]+", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-")
    return name[:256] if name else "subscriber-topic"


def ensure_subscriber_topic(
    sns,
    *,
    subscriber_id: int,
    subscriber_email: str,
    app_prefix: str,
) -> str:
    """
    Ensures a per-subscriber topic exists and (re)attempts email subscription.

    Notes:
    - create_topic is idempotent per Name.
    - subscribe(email) will send a confirmation email if not yet confirmed.
    - In production, you typically track subscriptions to avoid repeated pending subscriptions.
    """
    topic_name = _safe_topic_name(f"{app_prefix}-subscriber-{subscriber_id}")
    resp = sns.create_topic(Name=topic_name)
    topic_arn = resp["TopicArn"]

    sns.subscribe(
        TopicArn=topic_arn,
        Protocol="email",
        Endpoint=subscriber_email,
        ReturnSubscriptionArn=True,
    )
    return topic_arn


def publish_to_topic(sns, *, topic_arn: str, subject: str, body: str) -> None:
    sns.publish(
        TopicArn=topic_arn,
        Subject=subject[:100],
        Message=body,
    )


def format_subject(event: EarthquakeEvent) -> str:
    return f"Earthquake alert: M{event.magnitude:.1f} (country_id={event.country_id})"


def format_body(event: EarthquakeEvent) -> str:
    place = f"\nLocation: {event.place}" if event.place else ""
    return (
        "An earthquake has been recorded.\n\n"
        f"Earthquake ID: {event.earthquake_id}\n"
        f"Time: {event.occurred_at}\n"
        f"Country ID: {event.country_id}\n"
        f"Magnitude: {event.magnitude}\n"
        f"{place}\n"
    )


# -------------------------
# Service entrypoint (Lambda calls this)
# -------------------------

def handle_earthquake_alert(
    event: EarthquakeEvent,
    *,
    schema: str = "alpha",
    subscriber_table: str = "subscribers",
    auto_provision_topics: bool = True,
    app_topic_prefix: Optional[str] = None,
    sns_client=_SNS,
) -> Dict[str, Any]:
    """
    Main unit of work: DB fetch -> match -> ensure topic -> publish.
    Returns metrics for logging / response bodies.
    """
    if app_topic_prefix is None:
        app_topic_prefix = ENV.get("APP_TOPIC_PREFIX", "earthquake-alerts")

    with get_pg_connection() as conn:
        subs = fetch_subscribers(conn, schema=schema, table=subscriber_table)
        matched = [s for s in subs if matches(s, event)]

        if not matched:
            return {"matched": 0, "published": 0, "provisioned": 0}

        subject = format_subject(event)
        body = format_body(event)

        provisioned = 0
        published = 0

        for s in matched:
            topic_arn = s.sns_topic_arn

            if not topic_arn and auto_provision_topics:
                topic_arn = ensure_subscriber_topic(
                    sns_client,
                    subscriber_id=s.subscriber_id,
                    subscriber_email=s.subscriber_email,
                    app_prefix=app_topic_prefix,
                )
                update_subscriber_topic_arn(
                    conn,
                    schema=schema,
                    table=subscriber_table,
                    subscriber_id=s.subscriber_id,
                    topic_arn=topic_arn,
                )
                provisioned += 1

            if not topic_arn:
                continue

            publish_to_topic(sns_client, topic_arn=topic_arn,
                             subject=subject, body=body)
            published += 1

    return {"matched": len(matched), "published": published, "provisioned": provisioned}


# -------------------------
# Lambda handler
# -------------------------

def lambda_handler(event, context):
    """
    Lambda entrypoint.

    Expected JSON event structure (example):
    {
      "earthquake_id": 123,
      "country_id": 81,
      "magnitude": 3.2,
      "occurred_at": "2026-02-04T12:34:56Z",
      "place": "Near Tokyo",

      "schema": "alpha",
      "subscriber_table": "subscribers",
      "auto_provision_topics": true,
      "app_topic_prefix": "earthquake-alerts"
    }
    """
    event = event or {}

    # Extract configuration overrides (optional)
    schema = event.get("schema", "earthquakes")
    subscriber_table = event.get("subscriber_table", "subscribers")
    auto_provision_topics = bool(event.get("auto_provision_topics", True))
    app_topic_prefix = event.get("app_topic_prefix")  # may be None

    # Validate required earthquake payload
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
            schema=schema,
            subscriber_table=subscriber_table,
            auto_provision_topics=auto_provision_topics,
            app_topic_prefix=app_topic_prefix,
        )
    except Exception as e:
        # In production: log with structured logging and return a generic message
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
                "magnitude": eq.magnitude,
                **result,
            }
        ),
    }
