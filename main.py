from config import logger, settings
from database.helper import init_db_instance
from engine import core
from transformer import Agent


def main():
    logger.info("Starting the engine...")
    engine = core.Engine()
    logger.info("Running the process...")
    data = engine.run()

    if engine.status:
        logger.info("Transforming Data")
        df = Agent(data).transform()
        conn = init_db_instance()
        logger.info("Saving data into database...")
        logger.info(f"\n{df}")
        conn.insert_table(df, settings.OUTPUT_TABLE)
        logger.info("Application completed successfully")
    else:
        logger.error("Error encountered. Exiting...")


if __name__ == "__main__":
    main()
