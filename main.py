import logging

class CustomTextractException(Exception):
    """Exception class for errors in the textract processing pipeline."""
    def __init__(self, error_type, original_exception):
        super().__init__(f"{error_type} error: {str(original_exception)}")
        self.original_exception = original_exception

class Textractor:
    def load(self):
        try:
            self.extract_figures()
            self.extract_tables()
            self.extract_raw_text()
            image_summary, image_uuid = self.ingest_image()
            table_summary, table_uuid = self.ingest_tables()
            raw_pages = self._custom_textract_text_loader()
        except Exception as e:
            error_type = e.__class__.__name__.replace("Error", "")
            logging.error(f"Error during {error_type.lower()} process", exc_info=True)
            raise CustomTextractException(error_type, e)

# Assuming other methods are implemented elsewhere within the class.
