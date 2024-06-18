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


class ClassifierContratacion(CLassifier):
    def __init__(self, source_folder):
        logging.debug(f"ClassifierContratacion processed {self.num_contratacion_pdfs} files")
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
        logging.debug(f"ClassifierAnuncio processed {self.num_anuncio_pdfs} files")

        pattern_contratacion = r'Anuncio de formalización'
        parent_folder = os.path.dirname(source_folder)
        target_folder = os.path.join(parent_folder, 'anuncio')

        super().__init__(source_folder, pattern_contratacion, target_folder)

        # Number of files in target folder. It needs to be calculated after the filtering because the target folder is created in the parent class
        self.num_anuncio_pdfs = len(os.listdir(target_folder))

class ClassifierFormalizacion(CLassifier):
    def __init__(self, source_folder):
        logging.debug(f"ClassifierFormalizacion processed {self.num_formalizacion_pdfs} files")

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