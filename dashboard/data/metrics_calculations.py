"""Functions to calculate key metrics"""


def total_quakes(df):
    """Total number of earthquakes in timeframe."""
    return int(len(df))


def max_magnitude(df):
    """Maximum recorded magnitude."""
    if df.empty:
        return "—"
    return round(df["magnitude_value"].max(), 2)


def average_magnitude(df):
    """Average magnitude."""
    if df.empty:
        return "—"
    return round(df["magnitude_value"].mean(), 2)


def deepest(df):
    """Deepest earthquake (km)."""
    if df.empty:
        return "—"

    depth_km = df["depth"] / 1000.0
    return round(depth_km.max(), 1)


def shallowest(df):
    """Shallowest earthquake (km)."""
    if df.empty:
        return "—"

    depth_km = df["depth"] / 1000.0
    depth_km = depth_km[depth_km >= 0]

    if depth_km.empty:
        return "—"

    return round(depth_km.min(), 1)


def countries_affected(df):
    """Number of unique countries affected."""
    if df.empty:
        return "—"
    return (df["country_id"].nunique())
