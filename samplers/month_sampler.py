import os
import random
import logging
from datetime import datetime

def setup_logging(log_dir, log_filename):
    log_path = os.path.join(log_dir, log_filename)
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s')

def files_sampler(list_mm_yyyy: list, num_files: int, log_dir: str):
    setup_logging(log_dir, 'month_sampler.log')
    mm_yyyy_num_files = {}
    total_files = 0

    for mm_yyyy in list_mm_yyyy:
        folder_path = f"pdfs_range_{mm_yyyy}/formalizacion"
        if os.path.exists(folder_path):
            pdfs = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
            mm_yyyy_num_files[mm_yyyy] = len(pdfs)
            total_files += len(pdfs)
            logging.debug(f"Counted {len(pdfs)} PDFs for {mm_yyyy}")
        else:
            mm_yyyy_num_files[mm_yyyy] = 0
            logging.warning(f"Folder {folder_path} does not exist. Assigned 0 PDFs for {mm_yyyy}")

    # Calculate the weight (proportion) of each month-year's files relative to the total number of files
    mm_yyyy_weight = {mm_yyyy: count / total_files if total_files > 0 else 0 for mm_yyyy, count in mm_yyyy_num_files.items()}
    logging.debug(f"Calculated weights for sampling: {mm_yyyy_weight}")

    # Determine the number of files to sample from each month-year based on the weights
    mm_yyyy_size = {mm_yyyy: int(num_files * weight) for mm_yyyy, weight in mm_yyyy_weight.items()}
    remaining_files = num_files - sum(mm_yyyy_size.values())

    # Adjust for any rounding errors to ensure the total sampled files equal num_files
    remaining_files = num_files - sum(mm_yyyy_size.values())
    if remaining_files > 0:
        for mm_yyyy in sorted(mm_yyyy_size, key=lambda k: mm_yyyy_weight[k], reverse=True):
            if remaining_files <= 0:
                break
            mm_yyyy_size[mm_yyyy] += 1
            remaining_files -= 1
    logging.debug(f"Sample sizes adjusted: {mm_yyyy_size}")


    # Sample the files from each month-year directory
    mm_yyyy_sampled_files = {}
    for mm_yyyy, size in mm_yyyy_size.items():
        folder_path = f"pdfs_range_{mm_yyyy}/formalizacion"
        if os.path.exists(folder_path):
            pdfs = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
            if size > len(pdfs):
                size = len(pdfs)
            mm_yyyy_sampled_files[mm_yyyy] = random.sample(pdfs, size)
            logging.debug(f"Sampled {size} files for {mm_yyyy}")
        else:
            mm_yyyy_sampled_files[mm_yyyy] = []
            logging.warning(f"Folder {folder_path} does not exist. No files sampled for {mm_yyyy}")