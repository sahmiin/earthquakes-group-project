"""This script contains helper functions to handle the SES sender for the weekly report."""

import logging
from os import environ as ENV

import boto3
from email.message import EmailMessage

logging.basicConfig(level=logging.INFO)

SES_CLIENT = boto3.client("ses", region_name=ENV.get("AWS_REGION"))
SENDER = ENV.get("SES_SENDER")

def send_report_email(recipients: list, pdf_path: str, report_date: str):
    """Sends the weekly earthquake report PDF via AWS SES."""

    if not recipients:
        logging.warning("No recipients provided, skipping email.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"Weekly Earthquake Report – {report_date}"
    msg["From"] = SENDER
    msg["To"] = ", ".join(recipients)
    
    msg.set_content(f"""
                    Hello,
                    
                    We hope you are well! Attached is your weekly earthquake report.

                    Kind regards,
                    [Group Name]
                    """)

    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        msg.add_attachment(
            pdf_bytes,
            maintype="application",
            subtype="pdf",
            filename=f"earthquake_report_{report_date}.pdf"
        )
    except Exception as e:
        logging.error(f"Failed to read or attach PDF: {e}")
        raise

    try:
        SES_CLIENT.send_raw_email(
            Source=SENDER,
            Destinations=recipients,
            RawMessage={"Data": msg.as_bytes()}
        )
        logging.info(f"Email sent to {len(recipients)} recipients.")
    except Exception as e:
        logging.error(f"Failed to send email via SES: {e}")
        raise
