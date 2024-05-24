import time
import threading
from main_download import main as download_main
from samplers.month_sampler import files_sampler
from main_extract import main as extract_main

# Define start and end years
start_year = 2015
end_year = 2018

# List of months in the format mm-yyyy
list_mm_yyyy = [f"{mm_yyyy:02d}-{year}" for year in range(start_year, end_year) for mm_yyyy in range(1, 13)]
num_files = 200  # Number of files to sample

def ask_for_confirmation():
    global continue_script
    continue_script = None

    def get_user_input():
        global continue_script
        user_input = input("Do you want to continue? (y/n): ").strip().lower()
        if user_input == 'y':
            continue_script = True
        elif user_input == 'n':
            continue_script = False

    input_thread = threading.Thread(target=get_user_input)
    input_thread.start()
    input_thread.join(timeout=10)

    if continue_script is None:
        print("No response in 10 seconds, continuing...")
        return True
    return continue_script

def wait_and_check_continue():
    global continue_script
    continue_script = None

    def get_user_input():
        global continue_script
        user_input = input("Press 'y' to continue immediately: ").strip().lower()
        if user_input == 'y':
            continue_script = True

    input_thread = threading.Thread(target=get_user_input)
    input_thread.start()

    sleep_seconds = int(input("How many seconds to wait before continuing? "))
    for _ in range(sleep_seconds):
        time.sleep(1)
        if continue_script:
            break

    if continue_script:
        print("Continuing immediately...")
    else:
        print("Wait time completed, continuing...")

# Loop through the list of months
for mm_yyyy in list_mm_yyyy:
    # First create folders, download and classify files
    download_main(mm_yyyy)

    # Then sample the files
    mm_yyyy_sampled_files, mm_yyyy_size, mm_yyyy_weight = files_sampler(list_mm_yyyy, num_files)

    # Ask for confirmation to continue
    if not ask_for_confirmation():
        wait_and_check_continue()

    # Extract data
    for mm_yyyy, sampled_files in mm_yyyy_sampled_files.items():
        extract_main(mm_yyyy=mm_yyyy, sampled_files=sampled_files)
