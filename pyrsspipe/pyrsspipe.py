import argparse
import json
import logging
import os
from importlib import import_module

from pyrsspipe.makefeed import make_feed_wrapper
from pyrsspipe.validation import validate_feed_data


def pyrsspipe():
    pipeconfig_dir = os.getenv("PYRSSPIPE_PIPECONFIG_DIR")
    log_dir = os.getenv("PYRSSPIPE_LOG_DIR")

    # Initialize logger
    logging.basicConfig(
        level=logging.INFO,
        encoding="utf-8",
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "pyrsspipe.log")),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger()

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--pipeconfig", help="Specify the pipeconfig name", required=True
        )
        args = parser.parse_args()
        pipeconfig_name = args.pipeconfig
        logger.info(f"using pipeconfig {pipeconfig_name}")

        # Open the pipeconfig file

        pipeconfig_path = f"{pipeconfig_dir}/{pipeconfig_name}.json"
        with open(pipeconfig_path, "r") as file:
            pipeconfig = json.load(file)
        logger.info(f"parsed pipeconfig {pipeconfig_name}")

        input_module_name = pipeconfig["input"]["module"]
        input_module = import_module(f"pyrsspipe.input.{input_module_name}")
        input_function = getattr(input_module, "get_feed_items")

        logger.info(
            f"imported input module {input_module}, using input function {input_function}"
        )

        feed_items = input_function(**pipeconfig["input"]["args"], logger=logger)

        feed_data = {
            "feed_name": pipeconfig["feed_name"],
            "feed_language": pipeconfig["feed_language"],
            "items_data": feed_items,
        }

        try:
            validate_feed_data(feed_data)
        except ValueError as e:
            logger.error(f"invalid feed_data: {e}")
            raise e

        feed_xml = make_feed_wrapper(feed_data)
        logger.info("feed_xml created")

        output_module_name = pipeconfig["output"]["module"]
        output_module = import_module(f"pyrsspipe.output.{output_module_name}")
        output_function = getattr(output_module, "write_feed")
        logger.info(
            f"imported output module {output_module}, using output function {output_function}"
        )

        output_function(feed_xml, **pipeconfig["output"]["args"], logger=logger)
        logger.info("output complete")

        logger.info("pyrsspipe complete")

    except Exception as e:
        logger.error(e)
        raise e
