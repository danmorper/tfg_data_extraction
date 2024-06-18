import random
import logging

# Setup logging
logging.basicConfig(filename='model_randomizer.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def randomize_model():
    model = random.choice(['llama3', 'phi3'])
    logging.debug(f"Randomly selected model: {model}")
    return model