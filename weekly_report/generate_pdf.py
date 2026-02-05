"""This script creates the HTML string complete with all data and outputs a PDF of the result."""

import logging

import pandas as pd
from xhtml2pdf import pisa
from dotenv import load_dotenv

from data import get_db_connection, fetch_earthquake_data, get_statistics, get_top_countries

logging.basicConfig(level=logging.INFO)

def inject_stats(template_html: str, stats: dict) -> str:
    """Inject summary statistics into the HTML template."""
    stats_html = f"""
    <h2>Summary</h2>
    <ul>
        <li>Total Earthquakes: {stats.get('total_earthquakes', 0)}</li>
        <li>Maximum Magnitude: {stats.get('max_magnitude', 'N/A')}</li>
        <li>Average Magnitude: {stats.get('average_magnitude', 'N/A')}</li>
        <li>Deepest: {stats.get('deepest', 'N/A')} km</li>
        <li>Shallowest: {stats.get('shallowest', 'N/A')} km</li>
        <li>Countries Affected: {stats.get('countries_affected', 0)}</li>
    </ul>
    """
    return template_html.replace("<!-- STATS_PLACEHOLDER -->", stats_html)


def inject_top_countries(template_html: str, top_countries_df: pd.DataFrame, top_n: int = 5) -> str:
    """Inject the table of top affected countries into the HTML template."""
    rows_html = ""
    for _, row in top_countries_df.head(top_n).iterrows():
        rows_html += f"<tr><td>{row['country_name']}</td><td>{row['quake_count']}</td></tr>"

    table_html = f"""
    <h2>Top {top_n} Affected Countries</h2>
    <table>
        <thead>
            <tr><th>Country</th><th>Number of Quakes</th></tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    return template_html.replace("<!-- TOP_COUNTRIES_PLACEHOLDER -->", table_html)


def generate_pdf(df: pd.DataFrame, template_path: str, output_path: str):
    """Generate a PDF report from a dataframe using an HTML template."""
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    stats = get_statistics(df)
    top_countries = get_top_countries(df)

    html = inject_stats(html, stats)
    html = inject_top_countries(html, top_countries)

    with open(output_path, "wb") as pdf_file:
        result = pisa.CreatePDF(src=html, dest=pdf_file)
    if result.err:
        logging.error("Error generating PDF.")
        raise Exception("PDF generation failed.")

    logging.info(f"PDF successfully generated at {output_path}")

if __name__ == '__main__':
    load_dotenv()
    conn = get_db_connection()
    quake_data = fetch_earthquake_data(conn)

    generate_pdf(
        df=quake_data,
        template_path="index.html",
        output_path="weekly_earthquake_report.pdf"
    )