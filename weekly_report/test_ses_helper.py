"""This script contains simple tests for the SES helper functions."""
# pylint: skip-file
from email.message import EmailMessage
from unittest.mock import patch

import ses_helper
from ses_helper import SES_CLIENT, SENDER, create_main_message, send_report_email


def test_create_main_message_no_subscribers(caplog):
    """Tests edge-case of no subscribers in database when trying to send an email."""
    msg = create_main_message([])

    assert msg is None
    assert "No recipients provided, skipping email." in caplog.text


def test_create_main_message_success(monkeypatch, fake_subscribers):
    """Tests if the main body of the email is successfully created."""
    monkeypatch.setattr(ses_helper, "SENDER", "reports@example.com")

    subscribers = [f['subscriber_email'] for f in fake_subscribers]

    msg = create_main_message(subscribers)

    assert isinstance(msg, EmailMessage)
    assert msg["From"] == "reports@example.com"
    assert msg["To"] == ", ".join(subscribers)
    assert msg["Subject"].startswith("Weekly Earthquake Report")

    body = msg.get_content()
    assert "weekly earthquake report" in body.lower()
    assert "tremorlytics team" in body.lower()


@patch("ses_helper.SES_CLIENT")
def test_send_report_email_success(mock_ses_client, temp_pdf, fake_subscribers, monkeypatch):
    """Tests if the report sends successfully."""
    monkeypatch.setenv("SES_SENDER", "reports@example.com")

    msg = EmailMessage()
    msg["From"] = "reports@example.com"
    msg["To"] = "test1@example.com"
    msg.set_content("Test email")

    subscribers = [
        sub["subscriber_email"] for sub in fake_subscribers
    ]

    send_report_email(
        msg=msg,
        pdf_path=temp_pdf,
        subscribers=subscribers,
    )

    mock_ses_client.send_raw_email.assert_called_once()
