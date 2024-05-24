import os
import random

def files_sampler(list_mm_yyyy: list, num_files: int):
    mm_yyyy_num_files = {}
    total_files = 0
    for mm_yyyy in list_mm_yyyy:
        pdfs = [f for f in os.listdir(f"pdfs_range_{mm_yyyy}/formalizacion") if f.endswith(".pdf")]
        mm_yyyy_num_files[mm_yyyy] = len(pdfs)
        total_files += len(pdfs)
    mm_yyyy_weight = {mm_yyyy: num_files/total_files for mm_yyyy, num_files in mm_yyyy_num_files.items()}

    mm_yyyy_size = {mm_yyyy: int(num_files*mm_yyyy_weight[mm_yyyy]) for mm_yyyy, num_files in mm_yyyy_num_files.items()}

    # Now we have the number of files to sample for each mm_yyyy
    # We will sample the files
    mm_yyyy_sampled_files = {}
    for mm_yyyy, size in mm_yyyy_size.items():
        pdfs = [f for f in os.listdir(f"pdfs_range_{mm_yyyy}/formalizacion") if f.endswith(".pdf")]
        mm_yyyy_sampled_files[mm_yyyy] = random.sample(pdfs, size)
    return mm_yyyy_sampled_files, mm_yyyy_size, mm_yyyy_weight