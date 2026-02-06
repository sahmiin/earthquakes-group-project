"""This script contains helper functions to handle the SES sender for the weekly report."""

import logging
from datetime import datetime
from os import environ as ENV

from boto3 import client
from botocore.config import Config
from email.message import EmailMessage

logging.basicConfig(level=logging.INFO)

SES_CLIENT = client("ses", config=Config(connect_timeout=240, retries={'max_attempts': 2}), 
                    region_name=ENV.get("AWS_REGION", "eu-west-2"))
SENDER = ENV.get("SES_SENDER")

def create_main_message(subscribers: list) -> EmailMessage:
    """Creates skeleton message for PDF to be attached to."""
    if not subscribers:
        logging.warning("No recipients provided, skipping email.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"Weekly Earthquake Report – {datetime.now()}"
    msg["From"] = SENDER
    msg["To"] = ", ".join(subscribers)
    
    msg.set_content(f"""
                    Hello ,
                    
                    We hope you are well! Attached is your weekly earthquake report.

                    Kind regards,
                    The Tremorlytics Team
                    """)
    
    return msg


def send_report_email(msg: EmailMessage, pdf_path: str, subscribers: str):
    """Sends the weekly earthquake report PDF via AWS SES."""
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        msg.add_attachment(
            pdf_bytes,
            maintype="application",
            subtype="pdf",
            filename=f"earthquake_report_{datetime.now()}.pdf"
        )
    except Exception as e:
        logging.error(f"Failed to read or attach PDF: {e}")
        raise

    SES_CLIENT.send_raw_email(
            Source=SENDER,
            Destinations=subscribers,
            RawMessage={"Data": msg.as_bytes()}
        )
    logging.info(f"Email sent to {len(subscribers)} recipients.")
