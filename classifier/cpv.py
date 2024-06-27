import os
import re
import PyPDF2
import logging

def extract_cpv_codes(file_path):
    """
    Extract CPV codes from the provided PDF file.
    :param file_path: Path to the PDF file.
    :return: List of CPV codes found in the PDF.
    """
    cpv_codes = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text_pdf = ''
        for page_num in range(num_pages):
            page_text = reader.pages[page_num].extract_text()
            text_pdf += page_text
        pattern = re.compile(r'\b\d{8}-\d\b')
        cpv_codes = pattern.findall(text_pdf)
    return cpv_codes

def should_remove_pdf(cpv_codes):
    """
    Determine if the PDF should be removed based on the CPV codes.
    :param cpv_codes: List of CPV codes.
    :return: True if the PDF should be removed, False otherwise.
    """
    return len(cpv_codes) > 1

def remove_invalid_pdfs_in_formalizacion_folder(mm_yyyy, log_dir):
    """Remove PDFs in the formalizacion folder that have more than one CPV."""
    # Set up logging
    logging.basicConfig(filename=os.path.join(log_dir, 'cpv.log'),
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formalizacion_folder = f"pdfs_range_{mm_yyyy}"  # Update with actual path
    if not os.path.exists(formalizacion_folder):
        logging.debug(f"Formalizacion folder {formalizacion_folder} does not exist")
        return

    for file in os.listdir(formalizacion_folder):
        if file.endswith('.pdf'):
            file_path = os.path.join(formalizacion_folder, file)
            cpv_codes = extract_cpv_codes(file_path)
            if should_remove_pdf(cpv_codes):
                os.remove(file_path)
                logging.debug(f"Removed file {file} from {formalizacion_folder} due to multiple CPV codes")