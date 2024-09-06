# PDF Document Data Extraction Project

This project aims to download, classify, sample, and extract data from PDF documents related to public sector contracts.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Workflow](#workflow)
- [Script Details](#script-details)
- [Usage Instructions](#usage-instructions)
- [Stored Data](#stored-data)
- 
## Overview

The project automates the process of downloading PDF files from a specific source, classifying the files into relevant categories, sampling files for further processing, and extracting specific data from the PDF files.

## Project Structure
```verbatim
pdf-data-extraction-project/
│
├── data/
│ ├── classify_time.csv
│ ├── formalizacion_data.csv
│ ├── formalizacion_data.json
│ ├── mm_yyyy_sampled_files.json
│ ├── mm_yyyy_size.json
│ ├── mm_yyyy_weight.json
│ ├── download_time.csv
│ └── fail_downloads.json
├── logs/
│ ├── main.log
│ ├── main_download.log
│ ├── main_classifier.log
│ ├── main_extract.log
│ └── other_log_files.log
├── pdfs_range_mm-yyyy/
│ ├── contratacion/
│ ├── anuncio/
│ ├── formalizacion/
├── scripts/
│ ├── main.py
│ ├── main_download.py
│ ├── main_classifier.py
│ ├── main_extract.py
│ ├── download.py
│ ├── classifier.py
│ ├── data_loader.py
│ ├── data_extractors.py
│ ├── model_randomizer.py
│ └── month_sampler.py
└── README.md
```

## Workflow

### 1. Download PDF Files

The process starts with downloading PDF files based on a specified date range. The file `xml_departamento_id_fecha.json` provides the necessary data to identify and download relevant files.

```python
{
        "file": "sumario-yyyymmdd.xml",
        "date": "dd/mm/yyyy",
        "departamentos": [
            {
                "departamento": "nombre del departamento",
                "items": [
                    [
                        "id",
                        "part of the URL, for example: /boe/dias/2012/10/02/pdfs/BOE-A-2012-12290.pdf"
                    ],
                    [
                        ...
                    ]
                ]
            }
        ]
    }

```
### 2. Classify PDF Files
The downloaded files are classified into different categories: Contratación (Public Procurement), Anuncio (Announcement), and Formalización (Formalization). Each category corresponds to a subdirectory within the directory for the relevant month and year.

```
pdfs_range_mm-yyyy/
│
├── contratacion/
│   ├── pdf_file_1.pdf
│   ├── pdf_file_2.pdf
│   ├── ...
│
├── anuncio/
│   ├── pdf_file_1.pdf
│   ├── pdf_file_2.pdf
│   ├── ...
│
└── formalizacion/
    ├── pdf_file_1.pdf
    ├── pdf_file_2.pdf
    ├── ...
```

All pdfs not related to public sector contrats are removed.
### 3.  Sample PDF Files
A random sampling of the PDF files is performed to optimize the data extraction process.

### 4. Data Extraction
Finally, specific data is extracted from the sampled PDF files and stored in structured formats for further analysis.

## Script Details

### Download pdfs (download/download.py)
Defines the `Download` class responsible for filtering dates, creating folders, generating URL lists, and downloading the PDF files.

```python
class Download:
    def __init__(self, start_date, end_date, mm_yyyy, log_dir):
        # Initialize attributes
    def filter_dates(self, data, start_date_bad_format, end_date_bad_format):
        # Filter the dates
    def create_folder(self):
        # Create the folder for PDFs
    def list_download(self):
        # Generate the list of URLs
    def download_data(self):
        # Download the files
```

**Important**: Ensure that download_time.csv only contains the following header:

```csv
start_date,end_date,number_requests,number_pdfs,time,execution_date
```

### Classify pdfs
`classifier/classifier.py` is a module for classifying PDF files based on specified patterns. It is triggered in `main_classifier.py`.

This module contains classes for classifying PDF files based on patterns in their text content.
It provides functionality to read PDFs, filter text, and move matching PDFs to designated folders.

Classes:
    - `Classifier`: Base class for classifying PDFs based on a given pattern.
    - `ClassifierContratacion`: Class for classifying PDFs related to public sector contracts.
    - `ClassifierAnuncio`: Class for classifying PDFs related to contract formalization announcements.
    - `ClassifierFormalizacion`: Class for classifying PDFs related to contract formalization.

Usage:
    - Instantiate one of the classifier classes with the source folder containing PDFs to classify.
    - The classifier will move PDFs matching the specified pattern to the designated target folder.

Attributes:
    - source_folder: The source folder containing the PDF files to be classified.
    - pattern: The pattern used to filter PDF text content.
    - target_folder: The target folder where matched PDFs will be moved.
    - execution_time: Time taken for classification process.
    - execution_date: Date and time of classification process execution.
    - Number of total all pdfs of the month, all pdfs related to public sector contrats, announcements and formalizations.
save_execution_time function saves the execution time of the three classes in classify_time.csv.
- Args:
    - `classifier_contratacion`: Instance of ClassifierContratacion.
    - `classifier_anuncio`: Instance of ClassifierAnuncio.
    - `classifier_formalizacion`: Instance of ClassifierFormalizacion.

The `classify_time.csv` file contains the following columns:
- `mm_yyyy`: Month and year of classified PDFs.
- `num_all_pdfs`: Total number of PDFs before classification.
- `time_contratacion`: Time taken for classifying public sector contract PDFs.
- `num_contratacion_pdfs`: Number of PDFs classified under public sector contracts.
- `time_anuncio`: Time taken for classifying contract formalization announcement PDFs.
- `num_anuncio_pdfs`: Number of PDFs classified as contract formalization announcements.
- `time_formalizacion`: Time taken for classifying contract formalization PDFs.
- `num_formalizacion_pdfs`: Number of PDFs classified as contract formalization documents.
- `execution_date`: Date and time of execution.

### samplers

#### model_randomizer

chooses between models `llama3` and `phi3` with equal probability.

#### month_sampler

The `files_sampler` function is designed to sample a specified number of PDF files from directories representing different month-year combinations (result of `download` and `classifier` module). The function ensures that the sampled files are proportionally distributed according to the number of files available in each month-year directory.

##### Parameters
- list_mm_yyyy: A list of strings representing month-year combinations (e.g., ["01-2021", "02-2021"]).
- num_files: An integer specifying the total number of PDF files to sample across all month-year directories.

##### Returns
The function returns a tuple containing three dictionaries:

- mm_yyyy_sampled_files: Contains the sampled PDF file names for each month-year.
- mm_yyyy_size: Contains the number of files to be sampled from each month-year.
- mm_yyyy_weight: Contains the weight (proportion) of each month-year in the total file count.

##### Detailed Explanation
1. File Counting:
    - The function iterates through each month-year in list_mm_yyyy and counts the number of PDF files in the corresponding directory pdfs_range_{mm_yyyy}/formalizacion.
    - It stores these counts in the mm_yyyy_num_files dictionary and computes the total number of files across all directories (total_files).
2. Weight Calculation:
    - The function calculates the weight of each month-year's files relative to the total number of files. This is stored in the mm_yyyy_weight dictionary.
3. Size Calculation:
    - Using the weights, the function determines the number of files to sample from each month-year (mm_yyyy_size).
4. Rounding Adjustment:
    - To ensure the total number of sampled files equals num_files, the function adjusts for any rounding errors by distributing any remaining files across the month-year directories with the highest weights.
5. File Sampling:
    - The function samples the determined number of files from each month-year directory. It ensures not to sample more files than are available in each directory.

### Data Extraction: tools

#### data_loader.py
The `PDFReader` module provides functionality to read and parse PDF documents, focusing on extracting and managing document parts based on numbered headings.

#### Class DocumentPart

Represents a part of the PDF document. It is used to store data.

##### Attributes:
- `text`: The text content of the document part.
- `metadata`: Metadata associated with the document part (e.g., filename, page number).

##### Methods:
- `__str__()`: Returns a string representation of the document part, showing the first 100 characters of the text and metadata.

#### Class PDFReader

Handles reading and parsing the PDF document.

##### Attributes:
- `pdf_path`: The path to the PDF file.
- `filename`: The name of the PDF file.
- `document_parts`: A list of `DocumentPart` objects representing different parts of the document.

##### Methods:
- `__init__(self, pdf_path)`: Initializes the PDFReader with the specified PDF path and reads the document.
- `_read_pdf(self)`: Reads the PDF and extracts document parts based on numbered headings.
- `get_part(self, part_number)`: Returns a specific part of the document by index.
- `get_certain_parts(self, num)`: Returns a specific document part based on predefined section headers.
- `__str__(self)`: Returns a string representation of all `DocumentPart` objects in the document.

### data_extractor.py
The `DataExtractor` module is designed to extract specific data from text segments related to contract documents. It uses the OpenAI API requesting data to a local url and is built on top of the `pydantic` library for data validation and modeling. It is actually triggered in `main_extract.py`

#### Pydantic classes to store and validate data

- `CompanyData`

- `FinancialData`

- `AdjudicadoraData`

- `TipoData`

- `TramitacionData`

### Class DataExtractor

The main class responsible for extracting data in JSON format from text using the OpenAI API to a local URL.

- Attributes: 
    - `model`: The model to use for the OpenAI API (default is "llama3").
    - `api_key`: The API key for the OpenAI service. *We don't need it because we are not actually using OpenAI services, but it is necessary to enter string*
    - `base_url`: The base URL for the OpenAI service.
    - `text_company`: The text segment containing the company information.
    - `text_amount`: The text segment containing the financial information.
    - `text_adjudicadora`: The text segment containing the adjudicadora information.
    - `text_tipo`: The text segment containing the contract type information.
    - `text_tramitacion`: The text segment containing the tramitacion information.
- Methods:
    - `__init__(self, model, api_key, base_url, text_company, text_amount, text_adjudicadora, text_tipo, text_tramitacion)`: Initializes the DataExtractor with the specified parameters.
    - `extract_company(self)`: Extracts the company name from the provided text.
    - `extract_amount(self)`: Extracts the contract amount and currency from the provided text.
    - `extract_adjudicadora(self)`: Extracts the adjudicadora and expediente from the provided text.
    - `extract_tipo(self)`: Extracts the type of contract from the provided text.
    - `extract_tramitacion(self)`: Extracts the tramitacion and procedimiento from the provided text.
    - `__str__(self)`: Returns a string representation of the extracted data.

## main.py
Pipeline to download, classify, sample, and extract data from PDF files organized by month and year.

The pipeline consists of the following main steps:

1. **Create folders and download files**: Downloads PDF files for specified months and years.
2. **Classify files**: Classifies the downloaded PDF files into different categories.
3. **Sample files randomly**: Samples a specified number of files randomly from the downloaded and classified files.
4. **Extract data**: Extracts relevant data from the sampled PDF files.

## Stored data

- `formalizacion_data.csv`: main csv that will be used for data analysis.
- `formalizacion_data.txt`: it stores all the values in the previous CSV along with the text from which data was extracted in order to validate its consistency
- `fail_downloads.json`: unsuccessful HTTP requests to https://boe.es
- `classify_time.csv`: time and number of files per month and per type of document.
