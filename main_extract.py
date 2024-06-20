import pandas as pd
import os
import json
import time
from tools.data_loader import PDFReader
from tools.data_extractors import DataExtractor
from samplers.model_randomizer import randomize_model
import logging

def main(mm_yyyy: str, sampled_files: list, log_dir: str):
    # Setup logging
    log_path = os.path.join(log_dir, 'main_extract.log')
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s')

    # Directory and file paths
    csv_file_path = "data/formalizacion_data.csv"
    json_file_path = "data/formalizacion_data.json"

    # Read existing data
    try:
        df = pd.read_csv(csv_file_path)
        pdfs_processed = df["pdf"].tolist()
    except Exception as e:
        logging.error(f"Failed to read CSV file: {e}")
        pdfs_processed = []

    # Read JSON data
    try:
        with open(json_file_path, 'r') as file:
            text_information = json.load(file)
    except Exception as e:
        logging.error(f"Failed to read JSON file: {e}")
        text_information = []

    pdfs = [f for f in sampled_files if f not in pdfs_processed]

    def delete_comma(text):
        return text.replace(",", "") if text else None

    # Initialize counter for saving JSON data periodically
    save_counter = 0

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

            new_text_information = {
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
            except Exception as e:
                logging.error(f"Failed to write to CSV file: {e}")

            # Update JSON
            text_information.append(new_text_information)
            
            # Increment the save counter
            save_counter += 1
            
            # Save JSON data every 3 iterations
            if save_counter >= 3:
                try:
                    with open(json_file_path, 'w') as file:
                        json.dump(text_information, file, indent=4)
                    save_counter = 0  # Reset the counter after saving
                    text_information = []  # Clear the list after saving
                    logging.info("JSON data saved")
                except Exception as e:
                    logging.error(f"Failed to write JSON file: {e}")

            logging.info(f"Data extracted and processed from {pdf} in {processing_time:.2f} seconds")

        except Exception as e:
            logging.error(f"Failed to process {pdf}: {e}")

    # Final save of JSON data
    try:
        with open(json_file_path, 'w') as file:
            json.dump(text_information, file, indent=4)
        logging.info("Final JSON data saved")
    except Exception as e:
        logging.error(f"Failed to write final JSON file: {e}")

################################################## END OF MAIN LOOP ##################################################

#256 mins 170 filas