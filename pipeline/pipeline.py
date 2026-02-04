"""Extract script"""
import logging
from extract import extract_data
from transform import transform
from load import run_load_script


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    "Runs Extract, Transform, Load scripts"
    records = extract_data()
    logger.info("extract complete: %d records", len(records))

    df = transform(records)
    logger.info("transform complete: %d rows", len(df))

    new_events = df.to_dict("records")

    run_load_script(new_events)
    logger.info("load complete")

    logger.info("pipeline finished successfully")


if __name__ == "__main__":
    run_pipeline()
