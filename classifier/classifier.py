import os
import re
import shutil
import PyPDF2

def read_pdf(file_path):
    """Reads PDF file and returns the text content."""
    with open(file_path, 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        text = ''
        for i in range(len(pdf.pages)):
            text += pdf.pages[i].extract_text()
    return text

def filter_text(text, pattern):
    """Finds all occurrences of the pattern in text."""
    return re.findall(pattern, text)

def filter_pdfs_by_pattern(pattern, source_folder, target_folder):
    """Filters PDFs by pattern and copies matching PDFs to a new directory.
    Possible patterns: r'A\. Contratación del Sector Público', r'Anuncio de formalización', r'Formalización del contrato'
    """
    # Create target directory if it does not exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    filtered_files = []
    for file in os.listdir(source_folder):
        if file.endswith('.pdf'):
            full_path = os.path.join(source_folder, file)
            text = read_pdf(full_path)
            matches = filter_text(text, pattern)
            if matches:
                # Print matched files and the found text
                print(f'{file}: {matches}')
                # move to target folder
                shutil.move(full_path, os.path.join(target_folder, file))
                filtered_files.append(file)
    return filtered_files