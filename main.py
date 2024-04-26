[11:10 PM] Deep, Akash (External)
    def extract_tables(self, doc_object):
        for page in doc_object.pages:
            for table in page.tables:
                self.process_table(table, page)
 
    def process_table(self, table, page):
        table_name = f'page_{page.page_num}_table_{len(self.tables) + 1}'
        cropped_image = self.crop_image(page.image, table.bbox, page.image.size)
        table_img_path = f'{self.doc_path}/tables/img/{table_name}.png'
        cropped_image.save(table_img_path)
 
        table_info = self.collect_table_info(table, table_name, table_img_path)
        self.tables.append(table_info)
 
        # Verify table layout by analyzing the cropped table image
        self.verify_table_layout(cropped_image, table_info)
 
    def verify_table_layout(self, cropped_image, table_info):
        layout_doc = self.analyze_document([TextractFeatures.LAYOUT])
        table_info['verification_layouts'] = [
            {'type': layout.layout_type, 'confidence': layout.confidence} for layout in layout_doc.layouts
        ]
        self.validate_tables(table_info)
[11:10 PM] Deep, Akash (External)
    def analyze_document(self, features):
        return self.extractor.start_document_analysis(
            file_source=self.doc_name,
            s3_upload_path=self.s3_upload_path,
            features=features)
