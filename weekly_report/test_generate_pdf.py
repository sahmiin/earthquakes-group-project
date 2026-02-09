"""This script contains tests for the PDF report generation functions."""

from generate_pdf import inject_stats, inject_top_countries


def test_inject_stats(df_earthquakes):
    """Tests that html replaces placeholder correctly."""
    template = "<html><!-- STATS_PLACEHOLDER --></html>"
    stats = {
        "total_earthquakes": 4,
        "max_magnitude": 6.1,
        "average_magnitude": 4.93,
        "deepest": 15.3,
        "shallowest": 5.0,
        "countries_affected": 2
    }

    html = inject_stats(template, stats)

    assert "<ul>" in html
    assert "Total Earthquakes: 4" in html
    assert "Maximum Magnitude: 6.1" in html
    assert "<!-- STATS_PLACEHOLDER -->" not in html


def test_inject_top_countries(df_earthquakes):
    """Tests that html replaces placeholder correctly."""
    template = "<html><!-- TOP_COUNTRIES_PLACEHOLDER --></html>"
    
    top_countries = (
        df_earthquakes.groupby("country_name")
        .size()
        .reset_index(name="quake_count")
        .sort_values("quake_count", ascending=False)
    )

    html = inject_top_countries(template, top_countries, top_n=2)

    assert "Top 2 Affected Countries" in html
    assert "United States of America" in html
    assert "Japan" in html
    assert "<table" in html
    assert "<!-- TOP_COUNTRIES_PLACEHOLDER -->" not in html
