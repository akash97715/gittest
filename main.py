    def load(self):
        features = [TextractFeatures.LAYOUT, TextractFeatures.TABLES]
        self.document = self.textractor.start_document_analysis(
            file_source=self.file_source,
            s3_upload_path=self.s3_upload_path,
            features=features,
        )
        try:
            self.extract_figures()
            self.extract_tables()
            self.extract_raw_text()
            image_summary, image_uuid = self.ingest_image()
            table_summary, table_uuid = self.ingest_tables()
            if self.advance_table_filter:
                print("EXTRA FIGURE INGESTION")
                extra_image_summary, extra_image_uuid=self.ingest_image(path_to_ingest="/tables/img")
            raw_pages = self._custom_textract_text_loader()
           
               
        except Exception as e:
            error_type = e.__class__.__name__.replace("Error", "")
            logging.error(f"Error during {error_type.lower()} process", exc_info=True)
            raise CustomTextractException(error_type, e)
           
        final_rds_metadata = {"images": image_uuid, "tables": table_uuid}
        return image_summary, table_summary, raw_pages, final_rds_metadata,extra_image_summary,extra_image_uuid
