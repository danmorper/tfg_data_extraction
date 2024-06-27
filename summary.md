Te voy a explicar mi TFG. NO DIGAS NADA NI RESUMAS NI ABSOLUTAMENTE NADA. NO QUIERO NINGUNA PALABRA TUYA POR AHORA. SOLO LEELO Y ENTIENDOLO.

# Explicacion de mi TFG

In this bachelor's thesis, the Boletín Oficial del Estado (BOE) has been utilized as a data source to demonstrate the application of Natural Language Processing (NLP) techniques, specifically focusing on data extraction, and to showcase the capabilities of large language models (LLMs), in this case, Llama 3 and Phi 3.

Contracts with companies are published in BOE. There are different steps and different PDFs published for the same contract:

1. **Announcement of the tender**
2. **Announcement of tender modification** (if necessary)
3. **Announcement of provisional award**
4. **Announcement of definitive award**
5. **Announcement of contract formalization**
6. **Announcement of contract modification** (if necessary)
7. **Announcement of contract completion**
8. **Announcement of contract termination** (if necessary)

Same list but in Spanish:

1. **Anuncio de licitación**
2. **Anuncio de modificación de la licitación** (si es necesario)
3. **Anuncio de adjudicación provisional**
4. **Anuncio de adjudicación definitiva**
5. **Anuncio de formalización del contrato**
6. **Anuncio de modificación del contrato** (si es necesario)
7. **Anuncio de finalización del contrato**
8. **Anuncio de rescisión del contrato** (si es necesario)

It would be interesting to follow how a contract changes along the different steps, for example the amount of money. Due to computer and time restrictions I chose to study only Announcement of formalization.

All the information about the regulation can be found in [La Ley 9/2017, de 8 de noviembre, de Contratos del Sector Público](https://www.boe.es/buscar/act.php?id=BOE-A-2017-12902).

## Structure of BOE XML Files

It is important to understand the structure of the XML files.

```verbatim
python
Sumario
|
|-- Meta
|   |-- pub
|   |-- ano
|   |-- fecha
|   |-- fechaInv
|   |-- fechaAnt
|   |-- fechaAntAnt
|   |-- fechaSig
|   |-- fechaPub
|   |-- pubDate
|
|-- diario (nbo)
|   |-- sumario_nbo (id)
|   |   |-- urlPdf (szBytes, szKBytes)
|   |
|   |-- seccion (num, nombre)
|       |-- departamento (nombre, etq)
|           |-- item (id)
|               |-- urlPdf
|               |-- urlHtm
|               |-- urlXml
```

From the XML files, we extract the \texttt{xml\_departamento\_id\_fecha.json} file, from which the whole workflow starts. 

In order to get the previously mentioned JSON file, first we need to download the XML files. I downloaded all the XML files from 1st January 2000 till 10th May 2024.

The data pipeline involves several key steps: downloading PDFs, classifying them based on the different steps (announcement, contract and formalization), and extracting specific data using Large Language Models (LLMs).


Te voy a pasar scripts, no digas nada solo entiendolos y luego te voy a pedir una tarea.

# Scripts

## main.py
```python
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
```

## main_comparison.py
```python
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
```
## main_download.py
```python
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
```

## main_extract.py

```python
import pandas as pd
import os
import json
import time
from tools.data_loader import PDFReader
from tools.data_extractors import DataExtractor
from samplers.model_randomizer import randomize_model
import logging

def main(mm_yyyy: str, sampled_files: list, log_dir: str, comparison=False):
    # Setup logging
    log_path = os.path.join(log_dir, 'main_extract.log')
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Corrected format string

    if comparison:
        logging.info(f"Starting extraction for {mm_yyyy} with {len(sampled_files)} PDFs for comparison")
        csv_file_path = "data/comparison.csv"
        txt_file_path = "data/comparison.txt"
    else:
        logging.info(f"Starting extraction for {mm_yyyy} with {len(sampled_files)} PDFs")
        # Directory and file paths
        csv_file_path = "data/formalizacion_data.csv"
        txt_file_path = "data/formalizacion_data.txt"

    # Read existing data
    try:
        df = pd.read_csv(csv_file_path)
        pdfs_processed = df["pdf"].tolist()
    except Exception as e:
        logging.error(f"Failed to read CSV file: {e}")
        pdfs_processed = []

    pdfs = [f for f in sampled_files if f not in pdfs_processed]

    def delete_comma(text):
        return text.replace(",", "") if text else None

    ################################################## MAIN LOOP ##################################################
    # Process each PDF
    logging.debug(f"Starting extraction for {mm_yyyy} with {len(pdfs)} PDFs")
    for pdf in pdfs:
        pdf_dir = f"pdfs_range_{mm_yyyy}/formalizacion"
        start_time = time.time()  # Start time measurement
        # Select model
        model = randomize_model(log_dir=log_dir)
        try:
            pdf_path = os.path.join(pdf_dir, pdf)
            pdf_reader = PDFReader(pdf_path=pdf_path, log_dir=log_dir)
            extracted_data = DataExtractor(
                model=model,
                text_company=pdf_reader.get_certain_parts(num=6),
                text_amount=pdf_reader.get_certain_parts(num=5),
                text_adjudicadora=pdf_reader.get_certain_parts(num=1),
                text_tipo=pdf_reader.get_certain_parts(num=2),
                text_tramitacion=pdf_reader.get_certain_parts(num=3),
                log_dir=log_dir
            )

            # Calculate processing time
            processing_time = time.time() - start_time

            # Prepare the new row to add to the CSV
            new_row = f"{pdf_reader.filename},{mm_yyyy},{delete_comma(extracted_data.company_name)},{extracted_data.amount},{delete_comma(extracted_data.currency)},{delete_comma(extracted_data.adjudicadora)},{delete_comma(extracted_data.tipo)},{delete_comma(extracted_data.tramitacion)},{delete_comma(extracted_data.procedimiento)},{extracted_data.model},{processing_time:.2f}"

            text_information = {
                "pdf": pdf_reader.filename,
                "company_name": {
                    delete_comma(extracted_data.company_name): extracted_data.text_company
                },
                "amount": {
                    extracted_data.amount: extracted_data.text_amount
                },
                "currency": {
                    delete_comma(extracted_data.currency): ""
                },
                "adjudicadora": {
                    delete_comma(extracted_data.adjudicadora): extracted_data.text_adjudicadora
                },
                "tipo": {
                    delete_comma(extracted_data.tipo): extracted_data.text_tipo
                },
                "tramitacion": {
                    delete_comma(extracted_data.tramitacion): extracted_data.text_tramitacion   
                },
                "procedimiento": {
                    delete_comma(extracted_data.procedimiento): ""
                },
                "model": {
                    "model": extracted_data.model
                }
            }

            # Update CSV
            try:
                with open(csv_file_path, "a") as file:
                    file.write("\n" + new_row)
                logging.info(f"Data saved in the CSV file: {csv_file_path}. The data is: {new_row}")
            except Exception as e:
                logging.error(f"Failed to write to CSV file: {e}")

            # Update TXT with the JSON data as string
            json_data = json.dumps(text_information, indent=4)
            try:
                with open(txt_file_path, 'a') as file:
                    file.write(json_data + ",\n")
                logging.info("JSON data saved in txt file")
            except Exception as e:
                logging.error(f"Failed to write JSON data in txt file: {e}")

            logging.info(f"Data extracted and processed from {pdf} in {processing_time:.2f} seconds")

        except Exception as e:
            logging.error(f"Failed to process {pdf}: {e}")

    # Final save of JSON data
    try:
        with open(txt_file_path, 'a') as file:  # Corrected file path
            file.write("]")  # Close the JSON array
        logging.info("Final JSON data saved")
    except Exception as e:
        logging.error(f"Failed to write final JSON file: {e}")

################################################## END OF MAIN LOOP ##################################################

```

## download.py
```python
import json
import os
import requests
import logging
import time
from datetime import datetime
import logging

def setup_logging(log_dir, log_filename):
    log_path = os.path.join(log_dir, log_filename)
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s')


class Download:
    def __init__(self, start_date, end_date, mm_yyyy, log_dir):
        setup_logging(log_dir, 'download.log')

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
            logging.error(f"Error parsing date: {e}")
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

        filtered_file = f'xml_id_fecha_filtered_{self.mm_yyyy}.json'
        with open(filtered_file, 'w') as f:
            json.dump(filtered_data, f, indent=4)
        logging.debug(f"Filtered dates and saved to {filtered_file}")

        return filtered_data
    
    def create_folder(self):
        folder = f"pdfs_range_{self.mm_yyyy}"
        if os.path.exists(folder):
            logging.debug(f"Folder {folder} already exists")
            return True
        else:
            os.makedirs(folder)
            logging.debug(f"Created folder {folder}")
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
        logging.debug(f"Prepared list of files to download: {len(to_download)} items")
        return to_download

    def has_been_executed(self):
        if not os.path.exists(self.csv_path):
            return False
        with open(self.csv_path, 'r') as f:
            for line in f:
                if self.mm_yyyy in line:
                    logging.debug(f"Data for {self.mm_yyyy} has already been downloaded")
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
                    time.sleep(0.5)  # Delay of 0.5 second between requests

                # End time
                time_end = time.time()
                time_elapsed = time_end - time_start
                logging.debug(f"Downloaded {len(to_download)} files for {self.mm_yyyy} in {time_elapsed} seconds.")
                # Save in download_time.csv. It has 7 columns: 
                # start_date,end_date,mm_yyyy,number_requests,number_pdfs,time,execution_date
                with open(self.csv_path, 'a') as f:
                    f.write(f"\n{self.start_date},{self.end_date},{self.mm_yyyy},{len(to_download)},{len(os.listdir(f'pdfs_range_{self.mm_yyyy}'))},{time_elapsed},{execution_date}")
                logging.debug(f"Saved download record for {self.mm_yyyy}")
```

## classifier.py

```python
import os
import re
import shutil
import PyPDF2
import time
import logging

def setup_logging(log_dir, log_filename):
    log_path = os.path.join(log_dir, log_filename)
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
class CLassifier:
    def __init__(self, source_folder, pattern, target_folder, log_dir):
        setup_logging(log_dir, 'classifier.log')

        start = time.time()
        self.source_folder = source_folder
        self.pattern = pattern
        self.target_folder = target_folder
        # Call the filter_pdfs_by_pattern method with the pattern
        self.filter_pdfs_by_pattern(self.pattern)
        end = time.time()
        self.execution_time = end - start

        # Get date and time like 'dd-mm-yyyy HH:MM:SS'
        self.execution_date = time.strftime('%Y-%m-%d %H:%M:%S')

    # Methods to read PDFs and filter text
    def read_pdf(self, file_path):
        """Reads PDF file and returns the text content."""
        logging.debug(f"Reading PDF: {file_path}")

        with open(file_path, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            text = ''
            for i in range(len(pdf.pages)):
                text += pdf.pages[i].extract_text()
        return text

    def filter_text(self, text, pattern):
        """Finds all occurrences of the pattern in text."""
        logging.debug(f"Filtering text with pattern: {pattern}")
        return re.findall(pattern, text)

    def filter_pdfs_by_pattern(self, pattern):
        """Filters PDFs by pattern and copies matching PDFs to a new directory.
        Possible patterns: r'A\. Contratación del Sector Público', r'Anuncio de formalización', r'Formalización del contrato'
        """
        # Create target directory if it does not exist
        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)
            logging.debug(f'Created target folder: {self.target_folder}')

            filtered_files = []
            for file in os.listdir(self.source_folder):
                if file.endswith('.pdf'):
                    full_path = os.path.join(self.source_folder, file)
                    text = self.read_pdf(full_path)
                    matches = self.filter_text(text, pattern)
                    if matches:
                        # move to target folder
                        shutil.move(full_path, os.path.join(self.target_folder, file))
                        filtered_files.append(file)
                        logging.debug(f"Moved file {file} to {self.target_folder}")
            # Add the number of filtered files to the log
            logging.debug(f"Filtered {len(filtered_files)} files with pattern {pattern}")
        else:
            logging.debug(f"Target folder {self.target_folder} already exists")



class ClassifierContratacion(CLassifier):
    def __init__(self, source_folder):
        logging.debug(f"ClassifierContratacion for {source_folder}")
        pattern_contratacion = r'A\. Contratación del Sector Público'
        target_folder = os.path.join(source_folder, 'contratacion')

        # Number of files in the source folder
        self.num_all_pdfs = len(os.listdir(source_folder))

        # Get mm_yyyy from the source folder
        self.mm_yyyy = source_folder.split('_')[-1]

        super().__init__(source_folder, pattern_contratacion, target_folder)

        # Number of files in the target folder. It needs to be calculated after the filtering because the target folder is created in the parent class
        self.num_contratacion_pdfs = len(os.listdir(target_folder))
        # Call the delete_source_folder method
        self.delete_source_folder()

    def delete_source_folder(self):
        """Deletes all pdfs in the source folder after filtering."""
        for file in os.listdir(self.source_folder):
            if file.endswith('.pdf'):
                os.remove(os.path.join(self.source_folder, file))
                logging.debug(f"Deleted file {file} from {self.source_folder}")

class ClassifierAnuncio(CLassifier):
    def __init__(self, source_folder):
        logging.debug(f"ClassifierAnuncio for {source_folder}")

        pattern_contratacion = r'Anuncio de formalización'
        parent_folder = os.path.dirname(source_folder)
        target_folder = os.path.join(parent_folder, 'anuncio')

        super().__init__(source_folder, pattern_contratacion, target_folder)

        # Number of files in target folder. It needs to be calculated after the filtering because the target folder is created in the parent class
        self.num_anuncio_pdfs = len(os.listdir(target_folder))

class ClassifierFormalizacion(CLassifier):
    def __init__(self, source_folder):
        logging.debug(f"ClassifierFormalizacion for {source_folder}")

        pattern_contratacion = r'Formalización del contrato'
        parent_folder = os.path.dirname(source_folder)
        target_folder = os.path.join(parent_folder, 'formalizacion')


        super().__init__(source_folder, pattern_contratacion, target_folder)

        # Number of files in target folder. It needs to be calculated after the filtering because the target folder is created in the parent class
        self.num_formalizacion_pdfs = len(os.listdir(target_folder))

# Save the execution time of the three classes in classify_time.csv with the following columns: mm_yyyy,num_all_pdfs,time_contratacion,num_contratacion_pdfs,time_anuncio,num_anuncio_pdfs,time_formalizacion,num_formalizacion_pdfs,execution_date
def save_execution_time(classifier_contratacion, classifier_anuncio, classifier_formalizacion):
    """Save the execution time of the three classes in classify_time.csv.

    Args:
        classifier_contratacion: Instance of ClassifierContratacion.
        classifier_anuncio: Instance of ClassifierAnuncio.
        classifier_formalizacion: Instance of ClassifierFormalizacion.
    """
    with open("data/classify_time.csv", 'a') as f:
        f.write(f"\n{classifier_contratacion.mm_yyyy},{classifier_contratacion.num_all_pdfs},{classifier_contratacion.execution_time},{classifier_contratacion.num_contratacion_pdfs},{classifier_anuncio.execution_time},{classifier_anuncio.num_anuncio_pdfs},{classifier_formalizacion.execution_time},{classifier_formalizacion.num_formalizacion_pdfs},{classifier_contratacion.execution_date}")
    logging.debug(f"Saved execution time for {classifier_contratacion.mm_yyyy}")
```

## model_randomizer.py
```python
import random
import logging
import os

def setup_logging(log_dir, log_filename):
    log_path = os.path.join(log_dir, log_filename)
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def randomize_model(log_dir):
    setup_logging(log_dir, 'model_randomizer.log')
    model = random.choice(['llama3', 'phi3'])
    logging.debug(f"Randomly selected model: {model}")
    return model


## month_sampler.py
python
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

    return mm_yyyy_sampled_files, mm_yyyy_size, mm_yyyy_weight
```

## data_extractors.py
```python
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
import os
import logging

# Set up logging
def setup_logging(log_dir: str, log_filename: str):
    log_path = os.path.join(log_dir, log_filename)
    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Define the Pydantic models for the data extracted
class CompanyData(BaseModel):
    company: str = Field(..., title="Company", description="The name of the company involved in the contract")

class FinancialData(BaseModel):
    amount: float = Field(
        default=...,
        title="Amount",
        description="The total amount of the contract")
    currency: str = Field(
        default=...,
        title="Currency",
        description="The currency of the contract amount"
    )

class AdjudicadoraData(BaseModel):
    adjudicadora: str = Field(..., title="Adjudicadora", description="The name of the Contracting Authority")
    expediente: str = Field(None, title="Expediente", description="The contract number")

class TipoData(BaseModel):
    tipo: str = Field(..., title="Tipo", description="The type of contract: Contrato de obras, Contrato de concesion de obras, Contrato de concesion Servicios, Contrato de suministro, Contrato de Servicios, Contrato Mixto, Contrato menor")

class TramitacionData(BaseModel):
    tramitacion: str = Field(..., title="Tramitacion", description="The type of procedure:  Ordinaria, Urgente, Emergencia")
    procedimiento: str = Field(None, title="Procedimiento", description="The procedure type: Abierto, Restringido, Negociado con publicidad, Negociado sin publicidad, Diálogo competitivo, Asociacion para la innovacion, Simplificado, Basado en un Acuerdo Marco, Sistema Dinamico de Adquisicion.")

# Define the DataExtractor class
class DataExtractor:
    def __init__(self, model = "llama3",api_key: str ='ollama', base_url="http://localhost:11434/v1", text_company: str = None, text_amount: str = None, text_adjudicadora: str = None, text_tipo: str = None, text_tramitacion: str = None, log_dir: str = "None"):
        # Setup logging
        setup_logging(log_dir, 'data_extractor.log')
        logging.debug(f"Initializing DataExtractor with model: {model}")

        self.model = model

        self.text_company = text_company
        self.text_amount = text_amount
        self.text_adjudicadora = text_adjudicadora
        self.text_tipo = text_tipo
        self.text_tramitacion = text_tramitacion
        self.client = instructor.patch(
            OpenAI(
                base_url=base_url,
                api_key=api_key,
            ),
            mode=instructor.Mode.JSON,
        )

        # Initialize the extracted data
        self.company_name = None
        self.amount = None
        self.currency = None
        self.adjudicadora = None
        self.expediente = None
        self.tipo = None
        self.tramitacion = None
        self.procedimiento = None

        if self.text_amount is not None:
            logging.debug("Extracting amount")
            try:

                self.extract_amount()
            except Exception as e:
                logging.debug(f"Error extracting amount: {e}")
                
        if self.text_company is not None:
            logging.debug("Extracting company name")
            try:
                self.extract_company()
            except Exception as e:
                logging.debug(f"Error extracting company name: {e}")
        
        if self.text_adjudicadora is not None:
            logging.debug("Extracting adjudicadora")
            try:
                self.extract_adjudicadora()
            except Exception as e:
                logging.debug(f"Error extracting adjudicadora: {e}")
        if self.text_tipo is not None:
            logging.debug("Extracting tipo")
            try:
                self.extract_tipo()
            except Exception as e:
                logging.debug(f"Error extracting tipo: {e}")
        if self.text_tramitacion is not None:
            logging.debug("Extracting tramitacion")
            try:
                self.extract_tramitacion()
            except Exception as e:
                logging.debug(f"Error extracting tramitacion: {e}")

    def extract_company(self):
        content = f"""
        Extract the name of the 'Contratista' from the following text:
        {self.text_company}.

        For example, if the text is

        c) Contratista: LIFE CARE S.L.d) Importe o canon de adjudicación: Importe neto: 402.347,60 euros

        The company name is LIFE CARE S.L.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_model=CompanyData,
            max_retries=3
        )
        self.company_name = response.company
        logging.debug(f"Extracted company name: {self.company_name}")

    def extract_amount(self):
        content = f"""
        Extract the total contract amount and its currency from the following text, normally it is referred to as "Importe total":
        {self.text_amount}

        Output should follow python float number, for example with "Importe total: 302.000,00 euros." the number would be 302000.00
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_model=FinancialData,
            max_retries=3
        )
        self.amount = response.amount
        self.currency = response.currency
        logging.debug(f"Extracted amount: {self.amount}, currency: {self.currency}")

    def extract_adjudicadora(self):
        content = f"""
        Extract the name of the Contracting Authority from the text. Normally it is referred to as "Organismo" or "Entidad adjudicadora". Extract also "Numero de expediente" if available. IT IS NOT A PERSON, IT IS AN INSTITUTION OF PUBLIC ADMINISTRATION. Example text:
        {self.text_adjudicadora}
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_model=AdjudicadoraData,
            max_retries=3
        )
        self.adjudicadora = response.adjudicadora
        #self.expediente = response.expediente
        logging.debug(f"Extracted adjudicadora: {self.adjudicadora}")

    def extract_tipo(self):
        content = f"""
        Extract the type of contract from the text. Normally it is referred to as "Objetivo de Contrato Tipo".
        The different types of contracts are: The type of contract: Contrato de obras, Contrato de concesion de obras, Contrato de concesion Servicios, Contrato de suministro, Contrato de Servicios, Contrato Mixto, Contrato menor
        Example text:
        {self.text_tipo}
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_model=TipoData,
            max_retries=3
        )
        self.tipo = response.tipo
        logging.debug(f"Extracted tipo: {self.tipo}")

    def extract_tramitacion(self):
        content = f"""
        Extract the "tramitacion" and "procedimiento" from the text.
        The types of "tramitacion" are: "Ordinaria", "Urgente", "Emergencia".
        The types of procedimiento are: "Abierto", "Restringido", "Negociado con publicidad", "Negociado sin publicidad", "Diálogo competitivo", "Asociacion para la innovacion", "Simplificado", "Basado en un Acuerdo Marco", "Sistema Dinamico de Adquisicion".
        Example text:
        {self.text_tramitacion}
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_model=TramitacionData,
            max_retries=3
        )
        self.tramitacion = response.tramitacion
        self.procedimiento = response.procedimiento
        logging.debug(f"Extracted tramitacion: {self.tramitacion}, procedimiento: {self.procedimiento}")

    def __str__(self) -> str:
        printed_text = f"""
        Company Name: {self.company_name}
        Amount: {self.amount} in  {self.currency}
        Adjudicadora: {self.adjudicadora}
        Expediente: {self.expediente}
        Tipo: {self.tipo}
        Tramitacion: {self.tramitacion}
        Procedimiento: {self.procedimiento}
        """
        return printed_text
```

## data_loader.py

```python
import PyPDF2
import re
import logging
import os
from datetime import datetime

# setup_logging function
def setup_logging(log_dir, log_filename):
    log_path = os.path.join(log_dir, log_filename)
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class DocumentPart:
    def __init__(self, text, metadata):
        self.text = text
        self.metadata = metadata
    def __str__(self):
        # This will return the first 100 characters of text and the metadata page number.
        return f"Part[{self.text}: {self.metadata}]"
    

class PDFReader:
    def __init__(self, pdf_path, log_dir):
        # Setup logging
        setup_logging(log_dir, 'pdf_reader.log')

        self.pdf_path = pdf_path
        self.filename = pdf_path.split("/")[-1]
        self.document_parts = []
        # self.chunk_size = chunk_size
        # self.overlap = overlap
        self._read_pdf()

    def _read_pdf(self):
        logging.debug(f"Reading PDF: {self.pdf_path}")

        with open(self.pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            full_text = ""
            for page_number in range(num_pages):
                page = pdf_reader.pages[page_number]
                page_content = page.extract_text() or ""
                full_text += page_content

            # Divide the text based on the numbered headings
            parts = re.split(r'(\d+\.\s+[^\n]+:\n)', full_text)
            if parts and parts[0].strip() == '':
                parts = parts[1:]  # Remove any leading empty strings from split

            # Remove title and introduction
            parts = parts[1:]
            # Join the heading with the following text
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    parts[i] += parts[i + 1]
            parts = parts[::2]
            for part in parts:
                # Save the previous section before starting a new one
                self.document_parts.append(DocumentPart(text=part.strip(), metadata={"filename": self.filename}))


    def get_part(self, part_number):
        if 0 <= part_number < len(self.document_parts):
            logging.debug(f"Retrieving part {part_number}")
            return self.document_parts[part_number]
        else:
            error_msg = f"Part number {part_number} is out of range. There are {len(self.document_parts)} parts in the document but part numbers start at 0, so the last part number is {len(self.document_parts) - 1}."
            logging.debug(error_msg)
            return None
    

    def get_certain_parts(self, num: int):
        num_text = {
            1: "1. Entidad adjudicadora:",
            2: "2. Objeto del contrato:",
            3: "3. Tramitación y procedimiento:",
            4: "4. Valor estimado del contrato:",
            5: "5. Presupuesto base de licitación",
            6: "6. Formalización del contrato:"
        }
        for part in self.document_parts:
            if num_text[num] in part.text:
                logging.debug(f"Found text for part {num}: {num_text[num]}")
                return part.text
        logging.debug(f"Part {num} not found in document.")
        return None
    def __str__(self):
        # Create a string representation of all DocumentPart objects in the document
        printed_text = ""
        for part in self.document_parts:
            printed_text += str(part) + "\n"
            printed_text += "-"*50 + "\n"
        return printed_text
```