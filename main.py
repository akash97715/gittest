    def load(self):
        self.extract_figures()
        self.extract_tables()
        self.extract_raw_text()
        image_summary,image_uuid=self.ingest_image()
        table_summary,table_uuid=self.ingest_tables()
        raw_pages=self._custom_textract_text_loader()
 
        final_rds_metadata={'images':image_uuid,'tables':table_uuid}
        return image_summary,table_summary,raw_pages,final_rds_metadata
