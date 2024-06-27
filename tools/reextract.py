import json
import pandas as pd
import os
import logging
from tools.data_loader import PDFReader
from tools.data_extractors import DataExtractor

# Setup logging
log_dir = 'logs_retry'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(filename=os.path.join(log_dir, 'retry_extraction.log'),
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Function to delete commas
def delete_comma(text):
    return text.replace(",", "") if text else None

# Load existing data
csv_file_path = "data/formalizacion_data.csv"
txt_file_path = "data/formalizacion_data.txt"

# Read the CSV file
try:
    df = pd.read_csv(csv_file_path)
except Exception as e:
    logging.error(f"Failed to read CSV file: {e}")
    df = pd.DataFrame()

# Read the JSON data from the txt file
try:
    with open(txt_file_path, 'r') as file:
        json_data = json.loads('[' + file.read().strip()[:-1] + ']')  # Remove the trailing comma and add opening and closing brackets
except Exception as e:
    logging.error(f"Failed to read JSON file: {e}")
    json_data = []

# Retry extraction for the rows with None values
for index, row in df.iterrows():
    pdf_filename = row['pdf']
    json_entry = next((entry for entry in json_data if entry['pdf'] == pdf_filename), None)

    if not json_entry:
        logging.warning(f"No matching JSON entry found for {pdf_filename}")
        continue

    # Extract the text parts from the JSON data
    text_company = json_entry['company_name'][list(json_entry['company_name'].keys())[0]]
    text_amount = json_entry['amount'][list(json_entry['amount'].keys())[0]]
    text_adjudicadora = json_entry['adjudicadora'][list(json_entry['adjudicadora'].keys())[0]]
    text_tipo = json_entry['tipo'][list(json_entry['tipo'].keys())[0]]
    text_tramitacion = json_entry['tramitacion'][list(json_entry['tramitacion'].keys())[0]]

    # Re-run the data extraction only for None values
    try:
        model = 'llama3'  # Assuming the model used initially
        pdf_path = os.path.join(f"pdfs_range_{row['mm_yyyy']}/formalizacion", pdf_filename)

        if pd.isnull(row['company_name']):
            try:
                pdf_reader = PDFReader(pdf_path=pdf_path, log_dir=log_dir)
                extracted_data = DataExtractor(
                    model=model,
                    text_company=text_company,
                    log_dir=log_dir
                )
                df.at[index, 'company_name'] = delete_comma(extracted_data.company_name)
                logging.info(f"Re-extracted company name for {pdf_filename}")
            except Exception as e:
                logging.error(f"Failed to re-extract company name for {pdf_filename}: {e}")

        if pd.isnull(row['amount']):
            try:
                pdf_reader = PDFReader(pdf_path=pdf_path, log_dir=log_dir)
                extracted_data = DataExtractor(
                    model=model,
                    text_amount=text_amount,
                    log_dir=log_dir
                )
                df.at[index, 'amount'] = extracted_data.amount
                df.at[index, 'currency'] = delete_comma(extracted_data.currency)
                logging.info(f"Re-extracted amount and currency for {pdf_filename}")
            except Exception as e:
                logging.error(f"Failed to re-extract amount and currency for {pdf_filename}: {e}")

        if pd.isnull(row['adjudicadora']):
            try:
                pdf_reader = PDFReader(pdf_path=pdf_path, log_dir=log_dir)
                extracted_data = DataExtractor(
                    model=model,
                    text_adjudicadora=text_adjudicadora,
                    log_dir=log_dir
                )
                df.at[index, 'adjudicadora'] = delete_comma(extracted_data.adjudicadora)
                logging.info(f"Re-extracted adjudicadora for {pdf_filename}")
            except Exception as e:
                logging.error(f"Failed to re-extract adjudicadora for {pdf_filename}: {e}")

        if pd.isnull(row['tipo']):
            try:
                pdf_reader = PDFReader(pdf_path=pdf_path, log_dir=log_dir)
                extracted_data = DataExtractor(
                    model=model,
                    text_tipo=text_tipo,
                    log_dir=log_dir
                )
                df.at[index, 'tipo'] = delete_comma(extracted_data.tipo)
                logging.info(f"Re-extracted tipo for {pdf_filename}")
            except Exception as e:
                logging.error(f"Failed to re-extract tipo for {pdf_filename}: {e}")

        if pd.isnull(row['tramitacion']):
            try:
                pdf_reader = PDFReader(pdf_path=pdf_path, log_dir=log_dir)
                extracted_data = DataExtractor(
                    model=model,
                    text_tramitacion=text_tramitacion,
                    log_dir=log_dir
                )
                df.at[index, 'tramitacion'] = delete_comma(extracted_data.tramitacion)
                df.at[index, 'procedimiento'] = delete_comma(extracted_data.procedimiento)
                logging.info(f"Re-extracted tramitacion and procedimiento for {pdf_filename}")
            except Exception as e:
                logging.error(f"Failed to re-extract tramitacion and procedimiento for {pdf_filename}: {e}")

    except Exception as e:
        logging.error(f"Failed to re-extract data for {pdf_filename}: {e}")
