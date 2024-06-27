# main.py
import os
import logging
import pandas as pd
from datetime import datetime
from main_download import main as download_main
from main_classifier import main as classify_main
from samplers.month_sampler import files_sampler
from main_extract import main as extract_main

# Create log directory
log_root = 'logs'
if not os.path.exists(log_root):
    os.makedirs(log_root)

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_dir = os.path.join(log_root, current_time)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
logging.basicConfig(filename=os.path.join(log_dir, 'main.log'),
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Year of interest
year = 2017
num_files = 50
import random

seed = 123
# Set the seed
random.seed(seed)
logging.info(f"Seed set to {seed}")

# Download and classify files
list_mm_yyyy = [f"{month:02d}-{year}" for month in range(1, 13)]
for mm_yyyy in list_mm_yyyy:
    classify_time_path = "data/classify_time.csv"
    if os.path.exists(classify_time_path):
        classify_time_df = pd.read_csv(classify_time_path)
    if mm_yyyy in classify_time_df["mm_yyyy"].values:
        logging.debug(f"{mm_yyyy} already classified")
        continue
    else:
        try:
            download_main(mm_yyyy, log_dir)
        except Exception as e:
            logging.error(f"Error downloading files: {e}")
        try:
            classify_main(mm_yyyy, log_dir)
        except Exception as e:
            logging.error(f"Error classifying files: {e}")

# Sample the files
try:
    mm_yyyy_sampled_files, mm_yyyy_size, mm_yyyy_weight = files_sampler(year, num_files, log_dir)
except Exception as e:
    logging.error(f"Error sampling files: {e}")

# Save sampling results
import json
with open("data/mm_yyyy_sampled_files_comparison.json", "w") as f:
    json.dump(mm_yyyy_sampled_files, f, indent=4)
with open("data/mm_yyyy_size_comparison.json", "w") as f:
    json.dump(mm_yyyy_size, f, indent=4)
with open("data/mm_yyyy_weight_comparison.json", "w") as f:
    json.dump(mm_yyyy_weight, f, indent=4)

# Extract data using both models
for mm_yyyy, sampled_files in mm_yyyy_sampled_files.items():
    for model in ["llama3", "phi3"]:
        try:
            extract_main(mm_yyyy=mm_yyyy, sampled_files=sampled_files, log_dir=log_dir, model=model, comparison=True)
        except Exception as e:
            logging.error(f"Error extracting data with model {model}: {e}")
