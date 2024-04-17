import argparse
import json
import logging
import os
from importlib import import_module

from pyrsspipe.makefeed import make_feed_wrapper
from pyrsspipe.validation import validate_feed_data

CONFIG_DIR = os.getenv('PRP_CONFIG_DIR_PATH')
LOG_DIR = os.getenv('PRP_LOG_DIR_PATH')

def pyrsspipe():
    # Initialize logger
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',  handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'pyrsspipe.log')),
        logging.StreamHandler()
    ])

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', help='Specify the config name', required=True)
        args = parser.parse_args()
        config_name = args.config
        logging.info(f'using config {config_name}')

        # Open the config file
        
        config_path = f'{CONFIG_DIR}/{config_name}.json'
        with open(config_path, 'r') as file:
            config = json.load(file)
        logging.info(f'parsed config {config_name}')

        input_module_name = config['input']['module']
        input_module = import_module(f"input.{input_module_name}")
        input_function = getattr(input_module, 'get_feed_items')
            
        logging.info(f'imported input module {input_module}, using input function {input_function}')

        feed_items = input_function(**config['input']['args'], logger=logging)

        feed_data = {
            'feed_name': config['feed_name'],
            'feed_filename': config['feed_filename'],
            'feed_language': config['feed_language'],
            'items_data': feed_items
        }

        try:
            validate_feed_data(feed_data)
        except ValueError as e:
            logging.error(f'invalid feed_data: {e}')
            raise e
        
        feed_xml = make_feed_wrapper(feed_data)
        logging.info('feed_xml created')

        output_module_name = config['output']['module']
        output_module = import_module(f"output.{output_module_name}")
        output_function = getattr(output_module, 'write_feed')
        logging.info(f'imported output module {output_module}, using output function {output_function}')

        output_function(feed_xml, **config['output']['args'], logger=logging)
        logging.info('output complete')
        
        logging.info('pyrsspipe complete') 

    except Exception as e:
        logging.error(e)
        raise e


