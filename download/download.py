import json
import os
import requests
import logging
import time
from datetime import datetime

class Download:
    def __init__(self, start_date, end_date, mm_yyyy):
        self.start_date = start_date
        self.end_date = end_date
        self.mm_yyyy = mm_yyyy
        self.csv_path = 'data/download_time.csv'
        # Read the data from the json file
        with open('xml_departamento_id_fecha.json') as f:
            self.data = json.load(f)

    def validate_and_create_date(self, date_str, date_format):
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError as e:
            print(f"Error parsing date: {e}")
            raise

    def filter_dates(self, data, start_date_bad_format, end_date_bad_format):
        date_format_data = '%d/%m/%Y'
        date_format_script = '%d-%m-%Y'

        if not self.validate_and_create_date(start_date_bad_format, date_format_script):
            raise ValueError(f"Invalid start date: {start_date_bad_format}")
        if not self.validate_and_create_date(end_date_bad_format, date_format_script):
            raise ValueError(f"Invalid end date: {end_date_bad_format}")
    
        start_date = datetime.strptime(start_date_bad_format, date_format_script)
        end_date = datetime.strptime(end_date_bad_format, date_format_script)

        filtered_data = [d for d in data if d['date'] != "date not found"]
        filtered_data = [d for d in filtered_data if start_date <= datetime.strptime(d['date'], date_format_data) <= end_date]


        with open(f'xml_id_fecha_filtered_{self.mm_yyyy}.json', 'w') as f:
            json.dump(filtered_data, f, indent=4)
        
        return filtered_data
    
    def create_folder(self):
        folder = f"pdfs_range_{self.mm_yyyy}"
        print(f"Creating folder {folder}")
        if os.path.exists(folder):
            return True
        else:
            os.makedirs(folder)
            return False

    def list_download(self):
        # Filter the data
        filtered_data = self.filter_dates(self.data, self.start_date, self.end_date)
        # to_download
        to_download = []
        for xml in filtered_data:
            departamentos = xml["departamentos"]
            for departamento in departamentos:
                ids_urls = departamento["items"]
                # Obtener directamente los IDs desde ids_urls sin usar lambda
                for id_url in ids_urls:
                    to_download.append(id_url)
        return to_download

    def has_been_executed(self):
        if not os.path.exists(self.csv_path):
            return False
        with open(self.csv_path, 'r') as f:
            for line in f:
                if self.mm_yyyy in line:
                    return True
        return False
    
    def download_data(self):
        if self.has_been_executed():
            logging.info(f"Data for {self.mm_yyyy} has already been downloaded.")
        else:
        
            # Save execution time with the format DD-MM-YYYY HH:MM:SS
            execution_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            # Start time
            time_start = time.time()

            to_download = self.list_download()
            
            # Create the folder
            was_created = self.create_folder()
            
            if was_created:
                logging.info(f"Folder pdfs_range_{self.mm_yyyy} already exists.")
            else:
                # Download the pdfs
                base_url = "https://boe.es" 
                # Download the pdfs
                for id_url in to_download:
                    url = id_url[1]
                    full_url = base_url + url
                    #print(f"Downloading {full_url}")
                    filename = full_url.split("/")[-1]
                    path = f"pdfs_range_{self.mm_yyyy}/{filename}"
                    try:
                        response = requests.get(full_url)
                        if response.status_code == 200:
                            with open(path, 'wb') as f:
                                f.write(response.content)
                            logging.info(f"Downloaded PDF {filename} successfully.")
                        else:
                            logging.warning(f"Failed to download {filename}: Status {response.status_code}")
                    except requests.RequestException as e:
                        with open("failed_downloads.json", "a") as f:
                            json.dump({"url": full_url, "error": str(e)}, f, indent=4)
                            logging.error(f"Failed to download {filename}: {e}")
                    time.sleep(0.8)  # Delay of 1 second between requests

                # End time
                time_end = time.time()
                time_elapsed = time_end - time_start
                print(f"Downloaded {len(to_download)} files, month {self.mm_yyyy} in {time_elapsed} seconds.")
                # Save in download_time.csv. It has 7 columns: 
                # start_date,end_date,mm_yyyy,number_requests,number_pdfs,time,execution_date
                with open(self.csv_path, 'a') as f:
                    f.write(f"\n{self.start_date},{self.end_date},{self.mm_yyyy},{len(to_download)},{len(os.listdir(f'pdfs_range_{self.mm_yyyy}'))},{time_elapsed},{execution_date}")