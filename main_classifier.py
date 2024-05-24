from classifier.classifier import ClassifierContratacion, ClassifierAnuncio, ClassifierFormalizacion, save_execution_time

def main(mm_yyyy: str):
    print(f'Classifying contratacion files for {mm_yyyy}...')
    source_folder_contratacion = f'pdfs_range_{mm_yyyy}'
    classifier_contratacion = ClassifierContratacion(source_folder=source_folder_contratacion)

    print(f'Classifying anuncio files for {mm_yyyy}...')
    source_folder_anuncio = f'pdfs_range_{mm_yyyy}/contratacion'
    classifier_anuncio = ClassifierAnuncio(source_folder=source_folder_anuncio)

    print(f'Classifying formalizacion files for {mm_yyyy}...')
    source_folder_formalizacion = f'pdfs_range_{mm_yyyy}/contratacion'
    classifier_formalizacion = ClassifierFormalizacion(source_folder=source_folder_formalizacion)

    save_execution_time(classifier_contratacion, classifier_anuncio, classifier_formalizacion)