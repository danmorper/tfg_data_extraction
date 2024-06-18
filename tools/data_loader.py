# Read pdf
import PyPDF2
import re
import logging

# Setup logging
logging.basicConfig(filename='data_loader.log', 
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class DocumentPart:
    def __init__(self, text, metadata):
        self.text = text
        self.metadata = metadata
    def __str__(self):
        # This will return the first 100 characters of text and the metadata page number.
        return f"Part[{self.text}: {self.metadata}]"
    

class PDFReader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.filename = pdf_path.split("/")[-1]
        self.document_parts = []
        # self.chunk_size = chunk_size
        # self.overlap = overlap
        self._read_pdf()

    def _read_pdf(self):
        logging.debug(f"Reading PDF: {self.pdf_path}")

        with open(self.pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            full_text = ""
            for page_number in range(num_pages):
                page = pdf_reader.pages[page_number]
                page_content = page.extract_text() or ""
                full_text += page_content

            # Divide the text based on the numbered headings
            parts = re.split(r'(\d+\.\s+[^\n]+:\n)', full_text)
            if parts and parts[0].strip() == '':
                parts = parts[1:]  # Remove any leading empty strings from split

            # Remove title and introduction
            parts = parts[1:]
            # Join the heading with the following text
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    parts[i] += parts[i + 1]
            parts = parts[::2]
            for part in parts:
                # Save the previous section before starting a new one
                self.document_parts.append(DocumentPart(text=part.strip(), metadata={"filename": self.filename}))


    def get_part(self, part_number):
        if 0 <= part_number < len(self.document_parts):
            logging.debug(f"Retrieving part {part_number}")
            return self.document_parts[part_number]
        else:
            error_msg = f"Part number {part_number} is out of range. There are {len(self.document_parts)} parts in the document but part numbers start at 0, so the last part number is {len(self.document_parts) - 1}."
            logging.debug(error_msg)
            return None
    

    def get_certain_parts(self, num: int):
        num_text = {
            1: "1. Entidad adjudicadora:",
            2: "2. Objeto del contrato:",
            3: "3. Tramitación y procedimiento:",
            4: "4. Valor estimado del contrato:",
            5: "5. Presupuesto base de licitación",
            6: "6. Formalización del contrato:"
        }
        for part in self.document_parts:
            if num_text[num] in part.text:
                logging.debug(f"Found text for part {num}: {num_text[num]}")
                return part.text
        logging.debug(f"Part {num} not found in document.")
        return None
    def __str__(self):
        # Create a string representation of all DocumentPart objects in the document
        printed_text = ""
        for part in self.document_parts:
            printed_text += str(part) + "\n"
            printed_text += "-"*50 + "\n"
        return printed_text
    

