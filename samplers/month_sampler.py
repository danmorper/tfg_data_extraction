import os
import random

def files_sampler(list_mm_yyyy: list, num_files: int):
    mm_yyyy_num_files = {}
    total_files = 0

    # Count the number of PDF files in each specified month-year directory
    for mm_yyyy in list_mm_yyyy:
        pdfs = [f for f in os.listdir(f"pdfs_range_{mm_yyyy}/formalizacion") if f.endswith(".pdf")]
        mm_yyyy_num_files[mm_yyyy] = len(pdfs)
        total_files += len(pdfs)

    # Calculate the weight (proportion) of each month-year's files relative to the total number of files
    mm_yyyy_weight = {mm_yyyy: count / total_files for mm_yyyy, count in mm_yyyy_num_files.items()}

    # Determine the number of files to sample from each month-year based on the weights
    mm_yyyy_size = {mm_yyyy: int(num_files * weight) for mm_yyyy, weight in mm_yyyy_weight.items()}

    # Adjust for any rounding errors to ensure the total sampled files equal num_files
    remaining_files = num_files - sum(mm_yyyy_size.values())
    if remaining_files > 0:
        for mm_yyyy in sorted(mm_yyyy_size, key=lambda k: mm_yyyy_weight[k], reverse=True):
            if remaining_files <= 0:
                break
            mm_yyyy_size[mm_yyyy] += 1
            remaining_files -= 1

    # Sample the files from each month-year directory
    mm_yyyy_sampled_files = {}
    for mm_yyyy, size in mm_yyyy_size.items():
        pdfs = [f for f in os.listdir(f"pdfs_range_{mm_yyyy}/formalizacion") if f.endswith(".pdf")]
        if size > len(pdfs):  # Ensure that we do not try to sample more than available
            size = len(pdfs)
        mm_yyyy_sampled_files[mm_yyyy] = random.sample(pdfs, size)

    return mm_yyyy_sampled_files, mm_yyyy_size, mm_yyyy_weight
