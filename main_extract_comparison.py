import pandas as pd
import os
import json
import time
from tools.data_loader import PDFReader
from tools.data_extractors import DataExtractor
import logging

def main(mm_yyyy: str, sampled_files: list, log_dir: str):
    # Setup logging
    log_path = os.path.join(log_dir, 'main_extract.log')
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Corrected format string

    # Directory and file paths
    csv_file_path = "data/comparison.csv"
    txt_file_path = "data/comparison.txt"

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
    for model in ["llama3", "phi3"]:
        for pdf in pdfs:
            pdf_dir = f"pdfs_range_{mm_yyyy}/formalizacion"
            start_time = time.time()  # Start time measurement
            # Select model
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