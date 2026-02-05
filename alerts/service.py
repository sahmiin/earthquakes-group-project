"""Script containing functions to handle an earthquake alert"""
from __future__ import annotations

from dataclasses import replace
from os import environ as ENV

from .classes import EarthquakeEvent
from .queries import get_pg_connection, fetch_country_name, fetch_subscribers
from .preferences import matches
from .sns_client import build_filter_policy, subscribe_with_filter_policy, publish_event_once
from .formatting import format_subject, format_body


def handle_earthquake_alert(
    event: EarthquakeEvent,
    *,
    sns_client,
    topic_arn: str = None,
    subscribe_every_time: bool = True,
) -> dict[str, int | float]:
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
        country_name = fetch_country_name(conn, country_id=event.country_id)
        event = replace(event, country_name=country_name)
        subs = fetch_subscribers(conn)

    matched_count = sum(1 for s in subs if matches(s, event))

    subscribed_attempts = 0
    pending_confirmations = 0
    filter_policies_set = 0

    if subscribe_every_time:
        for s in subs:
            policy = build_filter_policy(s.country_id, s.magnitude_value)
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
        "pending_confirmations": int(pending_confirmations),
        "filter_policies_set": int(filter_policies_set),
    }
