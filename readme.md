Let's proceed with the data extraction. We have the file `xml_departamento_id_fecha.json`, which is a list of dictionaries with the following structure:

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

Now, let's proceed with downloading the desired PDFs.

Initially, a directory named `pdfs_range_mm-yyyy/` is created to contain all PDF files from a specific month and year. Subsequently, a subdirectory `contratacion/` is established within `pdfs_range_mm-yyyy/` to house PDFs associated with public sector contracts. These PDFs are identified by their content containing the phrase 'A Contratación del Sector Público'. Following the same method, two additional subdirectories, `anuncio/` and `formalizacion/`, are created within `pdfs_range_mm-yyyy/` to accommodate PDFs related to contract formalization announcements and contract formalization, respectively. This hierarchical organization results in the following folder structure:

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

# Download pdfs
In `download/download.py`, we define a class `Download` with the following attributes:
- Atributes
    1. start_date
    2. end_date
    3. mm_yyyy: month and year in which we download the data (start date is thought to be 1/mm/yyyy and end_date 31/mm/yyyy)
- methods:
    - filter_dates(self, data, start_date_bad_format, end_date_bad_format): Filters the data based on the given start and end dates.
    - create_folder(self): Creates a folder to save the downloaded PDFs.
    - list_download(self): Generates a list of URLs to download based on the filtered data.
    - download_data(self): Downloads the PDFs from the generated URLs and saves them to the appropriate folder.

We save `start_date`, `end_date`, `number_requests`, `number_pdfs`, `time` (in seconds), and `execution_date` in `download_time.csv` to keep track of every downloaded month.

**IMPORTANT TO ENSURE THAT `download_time.csv` ONLY CONTAINS THE FOLLOWING TEXT**
The rows are added with `\n` at the beggining.
```csv
start_date,end_date,number_requests,number_pdfs,time,execution_date
```

# Classify pdfs
`classifier/classifier.py` is a module for classifying PDF files based on specified patterns.

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
