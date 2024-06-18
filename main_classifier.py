from classifier.classifier import ClassifierContratacion, ClassifierAnuncio, ClassifierFormalizacion, save_execution_time
import logging

# Setup logging
logging.basicConfig(filename='main_classifier.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main(mm_yyyy: str):
    logging.debug(f'Starting classification for {mm_yyyy}')
    
    source_folder_contratacion = f'pdfs_range_{mm_yyyy}'
    logging.debug(f'Classifying contratacion files in {source_folder_contratacion}')
    classifier_contratacion = ClassifierContratacion(source_folder=source_folder_contratacion)

    source_folder_anuncio = f'pdfs_range_{mm_yyyy}/contratacion'
    logging.debug(f'Classifying anuncio files in {source_folder_anuncio}')
    classifier_anuncio = ClassifierAnuncio(source_folder=source_folder_anuncio)

    source_folder_formalizacion = f'pdfs_range_{mm_yyyy}/contratacion'
    logging.debug(f'Classifying formalizacion files in {source_folder_formalizacion}')
    classifier_formalizacion = ClassifierFormalizacion(source_folder=source_folder_formalizacion)

    save_execution_time(classifier_contratacion, classifier_anuncio, classifier_formalizacion)
    logging.debug(f'Finished classification for {mm_yyyy}')