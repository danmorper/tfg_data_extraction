# Create folders and download files
from main_download import main as download_main

# Classify files
from main_classifier import main as classify_main
# Sample files randomly
from samplers.month_sampler import files_sampler

# Extract data
from main_extract import main as extract_main

# Define start and end years
start_year = 2015
end_year = 2018
# List of months in the format mm-yyyy
list_mm_yyyy = [f"{mm_yyyy:02d}-{year}" for year in range(start_year, end_year) for mm_yyyy in range(1, 13)] # List of months in the format mm-yyyy
num_files = 300 # Number of files to sample

# First create folders, download and classify files
for mm_yyyy in list_mm_yyyy:
    download_main(mm_yyyy)
    classify_main(mm_yyyy)

# Sample the files
mm_yyyy_sampled_files, mm_yyyy_size, mm_yyyy_weight = files_sampler(list_mm_yyyy, num_files)

# Loop through the list of months amd extract the data
for mm_yyyy in list_mm_yyyy:
    print(f"-"*50)
    print(f"Processing {mm_yyyy}...")

    # Extract data
    for mm_yyyy, sampled_files in mm_yyyy_sampled_files.items():
            extract_main(mm_yyyy=mm_yyyy, sampled_files=sampled_files)
