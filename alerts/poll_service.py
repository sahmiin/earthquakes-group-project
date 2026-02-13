"""Scheduled polling alert service"""
from dataclasses import replace

from db_queries import fetch_subscribers, fetch_country_name, fetch_recent_earthquakes
from formatting import format_subject, format_body
from sns_client import (
    build_filter_policy,
    publish_event_once,
    list_topic_subscriptions_map,
    ensure_email_subscription_with_policy,
)


def handle_recent_earthquakes(
    conn,
    sns_client,
    topic_arn: str,
    subscribe_every_time: bool = True,
) -> dict:
    """Fetches recent earthquakes and subscribers matches them against policy filter"""
    subs = fetch_subscribers(conn)
    quakes = fetch_recent_earthquakes(conn)

    subscribed_attempts = 0
    pending_confirmations = 0
    filter_policies_set = 0
    already_subscribed = 0
    newly_subscribed = 0

    existing_map = list_topic_subscriptions_map(sns_client, topic_arn)

    if subscribe_every_time:
        for s in subs:
            policy = build_filter_policy(s.country_id, s.magnitude_value)

            prev_arn = existing_map.get(s.subscriber_email)
            sub_arn = ensure_email_subscription_with_policy(
                sns_client,
                topic_arn=topic_arn,
                email=s.subscriber_email,
                filter_policy=policy,
                existing_map=existing_map,
            )
            subscribed_attempts += 1

            if prev_arn:
                already_subscribed += 1
            else:
                newly_subscribed += 1
                if sub_arn:
                    existing_map[s.subscriber_email] = sub_arn

            if sub_arn and str(sub_arn).lower().startswith("pending"):
                pending_confirmations += 1
            elif sub_arn:
                filter_policies_set += 1

    published = 0
    for ev in quakes:
        country_name = fetch_country_name(conn, country_id=ev.country_id)
        ev = replace(ev, country_name=country_name)

        publish_event_once(
            sns_client,
            topic_arn=topic_arn,
            subject=format_subject(ev),
            body=format_body(ev),
            country_id=ev.country_id,
            magnitude=ev.magnitude,
        )
        published += 1

    return {
        "subscribers": len(subs),
        "earthquakes_found": len(quakes),
        "published_events": published,
        "subscribed_attempts": subscribed_attempts,
        "already_subscribed": already_subscribed,
        "newly_subscribed": newly_subscribed,
        "pending_confirmations": pending_confirmations,
        "filter_policies_set": filter_policies_set,
    }
