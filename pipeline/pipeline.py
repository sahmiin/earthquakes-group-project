"""Pipeline Script"""
import logging
from extract import extract_data
from transform import transform
from load import run_load_script
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    "Runs Extract, Transform, Load scripts"
    records = extract_data()
    logger.info("Extract complete: %d records", len(records))

    df = transform(records)
    logger.info("Transform complete: %d rows", len(df))

    new_events = df.to_dict("records")

    run_load_script(new_events)
    logger.info("Load complete!")

    logger.info("Pipeline finished successfully!")


def handler(event, context):
    load_dotenv()
    run_pipeline()
    return {
        "statusCode": 200,
        "body": "ETL pipeline completed successfully"
    }


if __name__ == "__main__":
    load_dotenv()
    run_pipeline()
