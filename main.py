class CustomTextractor:
    def __init__(self, file_source, doc_name, s3_upload_path,filename):
        self.file_source = file_source
        self.filename=filename
        self.doc_name = doc_name
        self.s3_upload_path = s3_upload_path
        self.extracted_figures = []
        self.extracted_tables = []
        self.document_text_layouts = []
        self.textractor = Textractor(profile_name="default")
        self.document = None  
 
    def start_analysis(self):
        features = [TextractFeatures.LAYOUT, TextractFeatures.TABLES]
        try:
            print("===============================file sent for analysis", self.file_source)
            self.document = self.textractor.start_document_analysis(
                file_source=self.file_source,
                s3_upload_path=self.s3_upload_path,
                features=features
            )
        except Exception as e:
            logging.error("Failed to start document analysis: %s", e)
            raise RuntimeError("Document analysis could not be started.") from e
 
    def extract_figures(self):
        if not self.document:
            self.start_analysis()
        for page in self.document.pages:
            self._process_page_for_figures(page)
 
    def _process_page_for_figures(self, page):
        figures_in_page = [layout for layout in page.layouts if layout.layout_type == 'LAYOUT_FIGURE']
        if figures_in_page:
            for index, figure in enumerate(figures_in_page):
                cropped_img = self._crop_image(page.image, figure.bbox, page.image.size)
                figure_path = self._save_cropped_image(cropped_img, "figures", f"page_{page.page_num}_figure_{index + 1}.jpg")
                figure_info = self._gather_figure_metadata(figure, figure_path, page.page_num)
                self.extracted_figures.append(figure_info)
 
    def extract_tables(self):
        if not self.document:
            self.start_analysis()
        for page in self.document.pages:
            self._process_page_for_tables(page)
 
    def _process_page_for_tables(self, page):
        if page.tables:
            for index, table in enumerate(page.tables):
                cropped_img = self._crop_image(page.image, table.bbox, page.image.size)
                table_img_path = self._save_cropped_image(cropped_img, "tables/img", f"page_{page.page_num}_table_{index + 1}.jpg")
                table_data = self._gather_table_metadata(table, table_img_path, page.page_num)
                self.extracted_tables.append(table_data)
 
    def extract_raw_text(self):
        if not self.document:
            self.start_analysis()
        for page in self.document.pages:
            #print("------page in the document is",page)
            self._process_page_for_text(page)
 
    def _process_page_for_text(self, page):
        page_full_text = page.text
        text_layouts_extracted = []
   
        for index, layout in enumerate(page.layouts):
            if layout.layout_type not in ['LAYOUT_FIGURE', 'LAYOUT_TABLE']:
                layout_data = {
                    "layout_id": layout.id,
                    "layout_name": f'page_{page.page_num}_layout_{index}',  # Adjusted to use the correct page number attribute
                    "layout_reading_order": layout.reading_order,
                    "layout_type": layout.layout_type,
                    "layout_text": layout.text,
                    "layout_confidence": layout.confidence,
                    "layout_width": layout.width,
                    "layout_height": layout.height,
                    "layout_x": layout.x,
                    "layout_y": layout.y,
                    "layout_page": page.page_num,  # Ensuring correct page number is referenced
                }
                text_layouts_extracted.append(layout_data)
   
        page_text_layout = {
            "document_name": self.doc_name,
            "page_num": page.page_num,  # Corrected
            "page_full_text": page_full_text,
            "text_layout_data": text_layouts_extracted
        }
   
        self.document_text_layouts.append(page_text_layout)
 
    def _crop_image(self, image, bbox, size):
        x, y, width, height = bbox.x * size[0], bbox.y * size[1], bbox.width * size[0], bbox.height * size[1]
        return image.crop((x, y, x + width, y + height))
 
    def _save_cropped_image(self, image, subdir, filename):
        path = os.path.join(self.doc_name, subdir)
        if not os.path.exists(path):
            os.makedirs(path)
        image_path = os.path.join(path, filename)
        image.save(image_path)
        return image_path
 
    def _gather_figure_metadata(self, figure, figure_path, page_num):
        return {
            "document_name": self.doc_name,
            "figure_id": figure.id,
            "figure_name": os.path.basename(figure_path),
            "figure_page": page_num,
            "figure_confidence": figure.confidence,
            "figure_bbox": figure.bbox,
            "figure_height": figure.height,
            "figure_width": figure.width,
            "figure_x": figure.x,
            "figure_y": figure.y,
            "figure_path": figure_path
        }
 
    def _gather_table_metadata(self, table, table_img_path, page_num):
        column_headers = [cell.text for cell in table.table_cells if cell.is_column_header]
        footers = [footer.text for footer in table.footers]
        #print("tables is=======================table",table)
        #print("tables is=======================table",help(table),dir(table))
        return {
            "document_name": self.doc_name,
            "table_id": table.id,
            "table_name": os.path.basename(table_img_path),
            "table_bbox": table.bbox,
            "table_column_count": table.column_count,
            "table_title": getattr(table.title, 'text', None),
            "column_headers": column_headers,
            "footers": footers,
            "table_height": table.height,
            "table_metadata": table.metadata,
            "table_page_number": page_num,
            "table_page_id": table.page_id,
            "table_confidence": table.raw_object['Confidence'],
            "table_row_count": table.row_count,
            "table_img_path": table_img_path,
            "table_html": table.to_html(),
            "table_markdown": table.to_markdown(),
            "table_width": table.width,
            "table_x": table.x,
            "table_y": table.y
        }
    def encode_image(self, img_path):
      with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
         
    def ingest_image(self):
        img_base64_list = []
        image_summaries = []
        img_ids = [str(uuid.uuid4()) for _ in self.extracted_figures]
        details_map = {item['figure_name']: item for item in self.extracted_figures}
        path=self.doc_name+'/figures'
 
       
 
        # Assuming 'path' is defined globally or within the class
        for img_file in sorted(os.listdir(path)):
            print("=========the path for image extraction",img_file)
            if img_file.endswith('.jpg'):
                img_path = os.path.join(path, img_file)
                print("=========the path for image extraction",img_path)
                base64_image = self.encode_image(img_path)
                img_base64_list.append(base64_image)
                if img_file in details_map:
                    details = details_map[img_file]
                    page_content = f"{self.filename} {details['figure_name']} page {details['figure_page']}"
                    metadata = {
                        "id_key": img_ids[sorted(os.listdir(path)).index(img_file)],  # Use sorted index
                        "document_name": self.filename,
                        "figure_name": details['figure_name']
                    }
                    image_summaries.append(Document(page_content=page_content, metadata=metadata))
        memory_store = S3DocStore(DOCS_BUCKET_NAME)
        memory_store.mset(list(zip(img_ids, img_base64_list)))
 
 
        return image_summaries, img_ids
    def ingest_tables(self):
       
        ghg_table = self.extracted_tables
        # Generate UUIDs for tables and images
        table_ids = [str(uuid.uuid4()) for _ in ghg_table]
       
        # Preparing metadata dict outside the loop for efficiency
        metadata_dict = {'doc_name': 'something', 'doc_md5': '14516542652'}
        # Summary table preparation
        summary_table = [
            Document(
                page_content=f"{self.filename} {item.get('table_page_number', '')} {item.get('table_title', '')} {' '.join(item.get('footers', []))}".strip(),
                metadata={
                    **metadata_dict,
                    'page_number': item.get('table_page_number', ''),
                    'document_name':self.filename,
                    'id_key': table_ids[index]
                }
            )
            for index, item in enumerate(ghg_table)
        ]
        memory_store = S3DocStore(DOCS_BUCKET_NAME)
        # HTML content extraction for tables
        html_content_list = [table['table_html'] for table in ghg_table]
        memory_store.mset(list(zip(table_ids, html_content_list)))
       
        return summary_table , table_ids
    def _custom_textract_text_loader(self):
        print("document content extracted from textract",self.document_text_layouts)
       
       
        pages = [
            Document(
                page_content=item['page_full_text'],
                metadata={
                    'page_number': item['page_num']
                     
                }
            )
            for index, item in enumerate(self.document_text_layouts)
        ]
        return pages
       
    def load(self):
        self.extract_figures()
        self.extract_tables()
        self.extract_raw_text()
        image_summary,image_uuid=self.ingest_image()
        table_summary,table_uuid=self.ingest_tables()
        raw_pages=self._custom_textract_text_loader()
 
        final_rds_metadata={'images':image_uuid,'tables':table_uuid}
        return image_summary,table_summary,raw_pages,final_rds_metadata
