import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
import os
import logging

# Set up logging
def setup_logging(log_dir: str, log_filename: str):
    log_path = os.path.join(log_dir, log_filename)
    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Define the Pydantic models for the data extracted
class CompanyData(BaseModel):
    company: str = Field(..., title="Company", description="The name of the company involved in the contract")

class FinancialData(BaseModel):
    amount: float = Field(
        default=...,
        title="Amount",
        description="The total amount of the contract")
    currency: str = Field(
        default=...,
        title="Currency",
        description="The currency of the contract amount"
    )

class AdjudicadoraData(BaseModel):
    adjudicadora: str = Field(..., title="Adjudicadora", description="The name of the Contracting Authority")
    expediente: str = Field(None, title="Expediente", description="The contract number")

class TipoData(BaseModel):
    tipo: str = Field(..., title="Tipo", description="The type of contract: Contrato de obras, Contrato de concesion de obras, Contrato de concesion Servicios, Contrato de suministro, Contrato de Servicios, Contrato Mixto, Contrato menor")

class TramitacionData(BaseModel):
    tramitacion: str = Field(..., title="Tramitacion", description="The type of procedure:  Ordinaria, Urgente, Emergencia")
    procedimiento: str = Field(None, title="Procedimiento", description="The procedure type: Abierto, Restringido, Negociado con publicidad, Negociado sin publicidad, Diálogo competitivo, Asociacion para la innovacion, Simplificado, Basado en un Acuerdo Marco, Sistema Dinamico de Adquisicion.")

# Define the DataExtractor class
class DataExtractor:
    def __init__(self, model = "llama3",api_key: str ='ollama', base_url="http://localhost:11434/v1", text_company: str = None, text_amount: str = None, text_adjudicadora: str = None, text_tipo: str = None, text_tramitacion: str = None, log_dir: str = "None"):
        # Setup logging
        setup_logging(log_dir, 'data_extractor.log')
        logging.debug(f"Initializing DataExtractor with model: {model}")

        self.model = model

        self.text_company = text_company
        self.text_amount = text_amount
        self.text_adjudicadora = text_adjudicadora
        self.text_tipo = text_tipo
        self.text_tramitacion = text_tramitacion
        self.client = instructor.patch(
            OpenAI(
                base_url=base_url,
                api_key=api_key,
            ),
            mode=instructor.Mode.JSON,
        )

        # Initialize the extracted data
        self.company_name = None
        self.amount = None
        self.currency = None
        self.adjudicadora = None
        self.expediente = None
        self.tipo = None
        self.tramitacion = None
        self.procedimiento = None

        if self.text_amount is not None:
            logging.debug("Extracting amount")
            try:

                self.extract_amount()
            except Exception as e:
                logging.debug(f"Error extracting amount: {e}")
                
        if self.text_company is not None:
            logging.debug("Extracting company name")
            try:
                self.extract_company()
            except Exception as e:
                logging.debug(f"Error extracting company name: {e}")
        
        if self.text_adjudicadora is not None:
            logging.debug("Extracting adjudicadora")
            try:
                self.extract_adjudicadora()
            except Exception as e:
                logging.debug(f"Error extracting adjudicadora: {e}")
        if self.text_tipo is not None:
            logging.debug("Extracting tipo")
            try:
                self.extract_tipo()
            except Exception as e:
                logging.debug(f"Error extracting tipo: {e}")
        if self.text_tramitacion is not None:
            logging.debug("Extracting tramitacion")
            try:
                self.extract_tramitacion()
            except Exception as e:
                logging.debug(f"Error extracting tramitacion: {e}")

    def extract_company(self):
        content = f"""
        Extract the name of the 'Contratista' from the following text:
        {self.text_company}.

        For example, if the text is

        c) Contratista: LIFE CARE S.L.d) Importe o canon de adjudicación: Importe neto: 402.347,60 euros

        The company name is LIFE CARE S.L.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_model=CompanyData,
            max_retries=3
        )
        self.company_name = response.company
        logging.debug(f"Extracted company name: {self.company_name}")

    def extract_amount(self):
        content = f"""
        Extract the total contract amount and its currency from the following text, normally it is referred to as "Importe total":
        {self.text_amount}

        Output should follow python float number, for example with "Importe total: 302.000,00 euros." the number would be 302000.00
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_model=FinancialData,
            max_retries=3
        )
        self.amount = response.amount
        self.currency = response.currency
        logging.debug(f"Extracted amount: {self.amount}, currency: {self.currency}")

    def extract_adjudicadora(self):
        content = f"""
        Extract the name of the Contracting Authority from the text. Normally it is referred to as "Organismo" or "Entidad adjudicadora". Extract also "Numero de expediente" if available. IT IS NOT A PERSON, IT IS AN INSTITUTION OF PUBLIC ADMINISTRATION. Example text:
        {self.text_adjudicadora}
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_model=AdjudicadoraData,
            max_retries=3
        )
        self.adjudicadora = response.adjudicadora
        #self.expediente = response.expediente
        logging.debug(f"Extracted adjudicadora: {self.adjudicadora}")

    def extract_tipo(self):
        content = f"""
        Extract the type of contract from the text. Normally it is referred to as "Objetivo de Contrato Tipo".
        The different types of contracts are: The type of contract: Contrato de obras, Contrato de concesion de obras, Contrato de concesion Servicios, Contrato de suministro, Contrato de Servicios, Contrato Mixto, Contrato menor
        Example text:
        {self.text_tipo}
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_model=TipoData,
            max_retries=3
        )
        self.tipo = response.tipo
        logging.debug(f"Extracted tipo: {self.tipo}")

    def extract_tramitacion(self):
        content = f"""
        Extract the "tramitacion" and "procedimiento" from the text.
        The types of "tramitacion" are: "Ordinaria", "Urgente", "Emergencia".
        The types of procedimiento are: "Abierto", "Restringido", "Negociado con publicidad", "Negociado sin publicidad", "Diálogo competitivo", "Asociacion para la innovacion", "Simplificado", "Basado en un Acuerdo Marco", "Sistema Dinamico de Adquisicion".
        Example text:
        {self.text_tramitacion}
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_model=TramitacionData,
            max_retries=3
        )
        self.tramitacion = response.tramitacion
        self.procedimiento = response.procedimiento
        logging.debug(f"Extracted tramitacion: {self.tramitacion}, procedimiento: {self.procedimiento}")

    def __str__(self) -> str:
        printed_text = f"""
        Company Name: {self.company_name}
        Amount: {self.amount} in  {self.currency}
        Adjudicadora: {self.adjudicadora}
        Expediente: {self.expediente}
        Tipo: {self.tipo}
        Tramitacion: {self.tramitacion}
        Procedimiento: {self.procedimiento}
        """
        return printed_text