Let's procede with the data extraction. We have the file `xml_departamento_id_fecha.json` which is a list of dictionaries with this structure:

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
                        "part of the url, for example: /boe/dias/2012/10/02/pdfs/BOE-A-2012-12290.pdf"
                    ],
                    [
                        ...
                    ]
                ]
            }
        ]
    },
```

Let's proceed downloading the desired pdfs. 

# Download pdfs
In `download/download.py` we define a class Download.
- Atributes
    1. start_date
    2. end_date
    3. mm_yyyy: month and year in which we download the data (start date is thought to be 1/mm/yyyy and end_date 31/mm/yyyy)
- methods:
    - filter_dates(self, data, start_date_bad_format, end_date_bad_format): Filters the data based on the given start and end dates.
    - create_folder(self): Creates a folder to save the downloaded PDFs.
    - list_download(self): Generates a list of URLs to download based on the filtered data.
    - download_data(self): Downloads the PDFs from the generated URLs and saves them to the appropriate folder.

We save start_date,end_date,number_requests,number_pdfs,time (in seconds),execution_date in `download_time.csv` to keep track of every downloaded month.

**IMPORTANT TO ASSURE THAT `download_time.csv` ONLY CONTAINS THE FOLLOWING TEXT**
```csv
start_date,end_date,number_requests,number_pdfs,time,execution_date
```