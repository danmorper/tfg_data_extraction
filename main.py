# Create folders and download files
from main_download import main as download_main

# Classify files
from main_classifier import main as classify_main
# Sample files randomly
from samplers.month_sampler import files_sampler

# Extract data
from main_extract import main as extract_main

import pandas as pd

# Create log directory
import os
from datetime import datetime
# Create log directory
log_root = 'logs'
if not os.path.exists(log_root):
    os.makedirs(log_root)

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_dir = os.path.join(log_root, current_time)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Pass log_dir to other scripts
log_dir_path = os.path.abspath(log_dir)
# Set up logging
import logging
logging.basicConfig(filename=os.path.join(log_dir, 'main.log'),
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Ask for start and end year
start_year = int(input("Enter start year: "))
end_year = int(input("Enter end year: "))
# List of months in the format mm-yyyy
list_mm_yyyy = [f"{mm_yyyy:02d}-{year}" for year in range(start_year, end_year+1) for mm_yyyy in range(1, 13)] # List of months in the format mm-yyyy
num_files = 300 # Number of files to sample

# First create folders, download and classify files
for mm_yyyy in list_mm_yyyy:
    # check if mm_yyyy is in data/classify_time.csv
    classify_time_path = "data/classify_time.csv"
    if os.path.exists(classify_time_path):
        classify_time_df = pd.read_csv(classify_time_path)
    if mm_yyyy in classify_time_df["mm_yyyy"].values:
        logging.debug(f"{mm_yyyy} already classified")
        continue
    else:
        try:
            download_main(mm_yyyy, log_dir_path)
        except Exception as e:
            logging.error(f"Error downloading files: {e}")
        try:
            classify_main(mm_yyyy, log_dir_path)
        except Exception as e:
            logging.error(f"Error classifying files: {e}")
# Sample the files
try:
    mm_yyyy_sampled_files, mm_yyyy_size, mm_yyyy_weight = files_sampler(list_mm_yyyy, num_files, log_dir_path)
except Exception as e:
    logging.error(f"Error sampling files: {e}")
# Save mm_yyyy_size, mm_yyyy_size and mm_yyyy_weight
import json
with open("data/mm_yyyy_sampled_files.json", "w") as f:
    json.dump(mm_yyyy_sampled_files, f, indent=4)
with open("data/mm_yyyy_size.json", "w") as f:
    json.dump(mm_yyyy_size, f, indent=4)
with open("data/mm_yyyy_weight.json", "w") as f:
    json.dump(mm_yyyy_weight, f, indent=4)

# Loop through the list of months amd extract the data
for mm_yyyy in list_mm_yyyy:
    logging.debug(f"-"*50)
    logging.debug(f"Processing {mm_yyyy}...")

    # Extract data
    for mm_yyyy, sampled_files in mm_yyyy_sampled_files.items():
        extract_main(mm_yyyy=mm_yyyy, sampled_files=sampled_files, log_dir=log_dir_path)

