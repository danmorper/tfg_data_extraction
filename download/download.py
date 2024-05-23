import json
import os
import requests
import logging
import time
from datetime import datetime

class Download:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.mm_yyyy = None
        
        # Read the data from the json file
        with open('xml_departamento_id_fecha.json') as f:
            self.data = json.load(f)

    def filter_dates(self, data, start_date_bad_format, end_date_bad_format):
        date_format = '%d/%m/%Y'
        start_date = datetime.strptime(start_date_bad_format, date_format)
        end_date = datetime.strptime(end_date_bad_format, date_format)

        filtered_data = [d for d in data if d['date'] != "date not found"]
        filtered_data = [d for d in filtered_data if start_date <= datetime.strptime(d['date'], date_format) <= end_date]

        # Construct filename directly
        mm_yyyy = start_date.strftime('%m-%Y')

        with open(f'xml_id_fecha_filtered_{mm_yyyy}.json', 'w') as f:
            json.dump(filtered_data, f, indent=4)
        
        return filtered_data, mm_yyyy
    
    def create_folder(self):
        folder = f"pdfs_range_{mm_yyyy}"
        if not os.path.exists(folder):
            os.makedirs(folder)


    def list_download(self):
        # Filter the data
        filtered_data, mm_yyyy = self.filter_dates(self.data, self.start_date, self.end_date)
        self.mm_yyyy = mm_yyyy
        # to_download
        to_download = []
        for xml in filtered_data:
            departamentos = xml["departamentos"]
            for departamento in departamentos:
                ids_urls = departamento["items"]
                # Obtener directamente los IDs desde ids_urls sin usar lambda
                for id_url in ids_urls:
                    to_download.append(id_url)
        return to_download, mm_yyyy

    def download_data(self):
        # Save execution time with the format DD-MM-YYYY HH:MM:SS
        execution_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        # Start time
        time_start = time.time()

        to_download, mm_yyyy = self.list_download()
        
        # Create the folder
        self.create_folder()
        
        # Download the pdfs
        base_url = "https://boe.es" 
        # Download the pdfs
        for id_url in to_download:
            url = id_url[1]
            full_url = base_url + url
            print(f"Downloading {full_url}")
            filename = full_url.split("/")[-1]
            path = f"pdfs_range_{mm_yyyy}/{filename}"
            try:
                response = requests.get(full_url)
                if response.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(response.content)
                    logging.info(f"Downloaded PDF {filename} successfully.")
                else:
                    logging.warning(f"Failed to download {filename}: Status {response.status_code}")
            except requests.RequestException as e:
                logging.error(f"Error downloading {filename}: {e}")

        # End time
        time_end = time.time()
        time_elapsed = time_end - time_start

        # Save in download_time.csv. It has 4 columns: 
        # start_date,end_date,number_requests,number_pdfs,time,execution_date
        with open('download_time.csv', 'a') as f:
            f.write(f"\n{self.start_date},{self.end_date},{len(to_download)},{len(os.listdir(f'pdfs_range_{mm_yyyy}'))},{time_elapsed},{execution_date}")
if __name__ == "__main__":
    start_date = "01/08/2012"
    end_date = "31/08/2012"
    download = Download(start_date, end_date)
    to_download, mm_yyyy = download.list_download()
    download.download_data()