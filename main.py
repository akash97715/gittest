class FigureExtractionError(Exception):
    pass

class TableExtractionError(Exception):
    pass

class TextExtractionError(Exception):
    pass

class ImageIngestionError(Exception):
    pass

class TableIngestionError(Exception):
    pass

class TextLoadingError(Exception):
    pass

import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def load(self):
    try:
        self.extract_figures()
    except Exception as e:
        logging.error("Error extracting figures", exc_info=True)
        raise FigureExtractionError from e

    try:
        self.extract_tables()
    except Exception as e:
        logging.error("Error extracting tables", exc_info=True)
        raise TableExtractionError from e

    try:
        self.extract_raw_text()
    except Exception as e:
        logging.error("Error extracting raw text", exc_info=True)
        raise TextExtractionError from e

    try:
        image_summary, image_uuid = self.ingest_image()
    except Exception as e:
        logging.error("Error ingesting image", exc_info=True)
        raise ImageIngestionError from e

    try:
        table_summary, table_uuid = self.ingest_tables()
    except Exception as e:
        logging.error("Error ingesting tables", exc_info=True)
        raise TableIngestionError from e

    try:
        raw_pages = self._custom_textract_text_loader()
    except Exception as e:
        logging.error("Error loading text", exc_info=True)
        raise TextLoadingError from e

    final_rds_metadata = {'images': image_uuid, 'tables': table_uuid}
    return image_summary, table_summary, raw_pages, final_rds_metadata
