"""This script is the main lambda handler for sending a weekly report."""

import logging
from datetime import datetime
from dotenv import load_dotenv

from data import get_db_connection, fetch_earthquake_data, fetch_subscribers
from generate_pdf import generate_pdf
from ses_helper import create_main_message, send_report_email

logging.basicConfig(level=logging.INFO)

def handler(event, context):
    """Handles main functionality of sending a weekly report."""
    conn = get_db_connection()
    quake_data = fetch_earthquake_data(conn)
    subs = fetch_subscribers(conn)

    generate_pdf(
        df=quake_data,
        template_path="index.html",
        output_path="/tmp/weekly_earthquake_report.pdf"
    )
    msg = create_main_message(subs)
    send_report_email(msg, '/tmp/weekly_earthquake_report.pdf', subs)
    logging.info("Email generation and sending process complete.")
    return {"status": "success"}
