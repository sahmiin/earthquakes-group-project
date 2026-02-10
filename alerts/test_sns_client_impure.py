"""Testing suite for impure functions in the sns_client script"""
import pytest
import json
from unittest.mock import Mock

from sns_client import (
    list_topic_subscriptions_map,
    ensure_email_subscription_with_policy,
    publish_event_once,
)


def test_list_topic_subscriptions_map_handles_pagination():
    sns = Mock()
    sns.list_subscriptions_by_topic.side_effect = [
        {
            "Subscriptions": [
                {"Endpoint": "a@example.com", "SubscriptionArn": "arn:sub:a"},
            ],
            "NextToken": "TOKEN",
        },
        {
            "Subscriptions": [
                {"Endpoint": "b@example.com", "SubscriptionArn": "arn:sub:b"},
            ],
        },
    ]

    m = list_topic_subscriptions_map(sns, "arn:topic")

    assert m == {"a@example.com": "arn:sub:a", "b@example.com": "arn:sub:b"}
    assert sns.list_subscriptions_by_topic.call_count == 2


def test_ensure_email_subscription_does_not_resubscribe_if_existing_confirmed():
    sns = Mock()
    existing = {"me@example.com": "arn:confirmed"}

    sub_arn = ensure_email_subscription_with_policy(
        sns,
        topic_arn="arn:topic",
        email="me@example.com",
        filter_policy={"country_id": ["81"]},
        existing_map=existing,
    )

    assert sub_arn == "arn:confirmed"
    sns.subscribe.assert_not_called()
    sns.set_subscription_attributes.assert_called_once()
    args, kwargs = sns.set_subscription_attributes.call_args
    assert kwargs["SubscriptionArn"] == "arn:confirmed"
    assert kwargs["AttributeName"] == "FilterPolicy"
    assert json.loads(kwargs["AttributeValue"]) == {"country_id": ["81"]}


def test_ensure_email_subscription_skips_policy_update_if_pending():
    sns = Mock()
    existing = {"me@example.com": "PendingConfirmation"}

    sub_arn = ensure_email_subscription_with_policy(
        sns,
        topic_arn="arn:topic",
        email="me@example.com",
        filter_policy={"magnitude": [{"numeric": [">=", 2.0]}]},
        existing_map=existing,
    )

    assert sub_arn == "PendingConfirmation"
    sns.subscribe.assert_not_called()
    sns.set_subscription_attributes.assert_not_called()


def test_ensure_email_subscription_subscribes_if_missing():
    sns = Mock()
    sns.subscribe.return_value = {"SubscriptionArn": "PendingConfirmation"}

    existing = {}
    sub_arn = ensure_email_subscription_with_policy(
        sns,
        topic_arn="arn:topic",
        email="new@example.com",
        filter_policy={},
        existing_map=existing,
    )

    assert sub_arn == "PendingConfirmation"
    sns.subscribe.assert_called_once()


def test_publish_event_once_sends_expected_message_attributes():
    sns = Mock()

    publish_event_once(
        sns,
        topic_arn="arn:topic",
        subject="Hello",
        body="Body",
        country_id=81,
        magnitude=3.2,
    )

    sns.publish.assert_called_once()
    _, kwargs = sns.publish.call_args

    assert kwargs["TopicArn"] == "arn:topic"
    assert kwargs["Subject"] == "Hello"
    assert kwargs["Message"] == "Body"
    attrs = kwargs["MessageAttributes"]
    assert attrs["country_id"]["DataType"] == "String"
    assert attrs["country_id"]["StringValue"] == "81"
    assert attrs["magnitude"]["DataType"] == "Number"
    assert attrs["magnitude"]["StringValue"].startswith("3.2")
