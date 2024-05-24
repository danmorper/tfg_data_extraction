import os
import re
import shutil
import PyPDF2
import time
class CLassifier:
    def __init__(self, source_folder, pattern, target_folder):
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
        with open(file_path, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            text = ''
            for i in range(len(pdf.pages)):
                text += pdf.pages[i].extract_text()
        return text

    def filter_text(self, text, pattern):
        """Finds all occurrences of the pattern in text."""
        return re.findall(pattern, text)

    def filter_pdfs_by_pattern(self, pattern):
        """Filters PDFs by pattern and copies matching PDFs to a new directory.
        Possible patterns: r'A\. Contratación del Sector Público', r'Anuncio de formalización', r'Formalización del contrato'
        """
        # Create target directory if it does not exist
        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)

        filtered_files = []
        for file in os.listdir(self.source_folder):
            if file.endswith('.pdf'):
                full_path = os.path.join(self.source_folder, file)
                text = self.read_pdf(full_path)
                matches = self.filter_text(text, pattern)
                if matches:
                    # Print matched files and the found text
                    print(f'{file}: {matches}')
                    # move to target folder
                    shutil.move(full_path, os.path.join(self.target_folder, file))
                    filtered_files.append(file)

class ClassifierContratacion(CLassifier):
    def __init__(self, source_folder):
        pattern_contratacion = r'A\. Contratación del Sector Público'
        target_folder = os.path.join(source_folder, 'contratacion')

        # Number of files in the source folder
        self.num_all_pdfs = len(os.listdir(source_folder))


        super().__init__(source_folder, pattern_contratacion, target_folder)

        # Number of files in the target folder. It needs to be calculated after the filtering because the target folder is created in the parent class
        self.num_contratacion_pdfs = len(os.listdir(target_folder))
        # Call the delete_source_folder method
        self.delete_source_folder()

        # Get mm_yyyy from the source folder
        self.mm_yyyy = source_folder.split('_')[-1]

    def delete_source_folder(self):
        """Deletes all pdfs in the source folder after filtering."""
        for file in os.listdir(self.source_folder):
            if file.endswith('.pdf'):
                os.remove(os.path.join(self.source_folder, file))

class ClassifierAnuncio(CLassifier):
    def __init__(self, source_folder):
        pattern_contratacion = r'Anuncio de formalización'
        parent_folder = os.path.dirname(source_folder)
        target_folder = os.path.join(parent_folder, 'anuncio')

        super().__init__(source_folder, pattern_contratacion, target_folder)

        # Number of files in target folder. It needs to be calculated after the filtering because the target folder is created in the parent class
        self.num_anuncio_pdfs = len(os.listdir(target_folder))

class ClassifierFormalizacion(CLassifier):
    def __init__(self, source_folder):
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
    with open("classify_time.csv", 'a') as f:
        f.write(f"\n{classifier_contratacion.mm_yyyy},{classifier_contratacion.num_all_pdfs},{classifier_contratacion.execution_time},{classifier_contratacion.num_contratacion_pdfs},{classifier_anuncio.execution_time},{classifier_anuncio.num_anuncio_pdfs},{classifier_formalizacion.execution_time},{classifier_formalizacion.num_formalizacion_pdfs},{classifier_contratacion.execution_date}")

# Test the three classes and save the execution time
source_folder_contratacion = 'pdfs_range_08-2016'
classifier_contratacion = ClassifierContratacion(source_folder=source_folder_contratacion)

source_folder_anuncio = 'pdfs_range_08-2016/contratacion'
classifier_anuncio = ClassifierAnuncio(source_folder=source_folder_anuncio)

source_folder_formalizacion = 'pdfs_range_08-2016/contratacion'
classifier_formalizacion = ClassifierFormalizacion(source_folder=source_folder_formalizacion)

save_execution_time(classifier_contratacion, classifier_anuncio, classifier_formalizacion)