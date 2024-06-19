from classifier.classifier import ClassifierContratacion, ClassifierAnuncio, ClassifierFormalizacion, save_execution_time
import os
import logging
from datetime import datetime

def main(mm_yyyy: str, log_dir: str):
    # Setup logging
    log_path = os.path.join(log_dir, 'main_classifier.log')
    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logging.debug(f'Starting classification for {mm_yyyy}')
    
    source_folder_contratacion = f'pdfs_range_{mm_yyyy}'
    logging.debug(f'Classifying contratacion files in {source_folder_contratacion}')
    classifier_contratacion = ClassifierContratacion(source_folder=source_folder_contratacion, log_dir=log_dir)

    source_folder_anuncio = f'pdfs_range_{mm_yyyy}/contratacion'
    logging.debug(f'Classifying anuncio files in {source_folder_anuncio}')
    classifier_anuncio = ClassifierAnuncio(source_folder=source_folder_anuncio, log_dir=log_dir)

    source_folder_formalizacion = f'pdfs_range_{mm_yyyy}/contratacion'
    logging.debug(f'Classifying formalizacion files in {source_folder_formalizacion}')
    classifier_formalizacion = ClassifierFormalizacion(source_folder=source_folder_formalizacion, log_dir=log_dir)

    save_execution_time(classifier_contratacion, classifier_anuncio, classifier_formalizacion)
    logging.debug(f'Finished classification for {mm_yyyy}')