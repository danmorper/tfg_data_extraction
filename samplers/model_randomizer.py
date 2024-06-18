import random
import logging
import os

def setup_logging(log_dir, log_filename):
    log_path = os.path.join(log_dir, log_filename)
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def randomize_model(log_dir):
    setup_logging(log_dir, 'model_randomizer.log')
    model = random.choice(['llama3', 'phi3'])
    logging.debug(f"Randomly selected model: {model}")
    return model
