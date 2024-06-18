from download.download import Download
import calendar
from datetime import datetime
import os
import logging

def main(mm_yyyy: str, log_dir: str):
    # Setup logging
    log_path = os.path.join(log_dir, 'main_download.log')
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    try:
        start_date = f"01-{mm_yyyy}"
        month, year = mm_yyyy.split("-")
        year = int(year)
        month = int(month)
        
        if not (1 <= month <= 12):
            raise ValueError(f"Invalid month: {month}")
        if year < 1900 or year > 2100:
            raise ValueError(f"Invalid year: {year}")
        
        end_day = calendar.monthrange(year, month)[1]
        end_date = f"{end_day:02d}-{mm_yyyy}"
        
        logging.debug(f"Creating download instance for {mm_yyyy} with dates {start_date} to {end_date}")
        download = Download(start_date, end_date, mm_yyyy, log_dir)
        download.download_data()
    except Exception as e:
        logging.error(f"Error downloading data for {mm_yyyy}: {e}")