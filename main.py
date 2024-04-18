import os

class DocumentAnalyzer:
    def __init__(self, extractor, file_source, doc_name, s3_upload_path):
        self.extractor = extractor
        self.file_source = file_source
        self.doc_name = doc_name
        self.s3_upload_path = s3_upload_path
        self.extracted_figures = []
        self.extracted_tables = []
        self.validated_tables = []

    def start_analysis(self, features):
        return self.extractor.start_document_analysis(file_source=self.file_source,
                                                      s3_upload_path=self.s3_upload_path,
                                                      features=features)

    def extract_figures(self):
        document = self.start_analysis([TextractFeatures.LAYOUT, TextractFeatures.TABLES])
        for page in document.pages:
            self._process_page_for_figures(page)

    def _process_page_for_figures(self, page):
        figures_in_page = [layout for layout in page.layouts if layout.layout_type == 'LAYOUT_FIGURE']
        if figures_in_page:
            for index, figure in enumerate(figures_in_page):
                cropped_img = self._crop_image(page.image, figure.bbox, page.image.size)
                figure_path = self._save_cropped_image(cropped_img, "figures", f"page_{page.page_num}_figure_{index + 1}.png")
                figure_info = self._gather_figure_metadata(figure, figure_path, page.page_num)
                self.extracted_figures.append(figure_info)

    def extract_tables(self):
        document = self.start_analysis([TextractFeatures.TABLES])
        for page in document.pages:
            self._process_page_for_tables(page)

    def _process_page_for_tables(self, page):
        if page.tables:
            for index, table in enumerate(page.tables):
                cropped_img = self._crop_image(page.image, table.bbox, page.image.size)
                table_img_path = self._save_cropped_image(cropped_img, "tables/img", f"page_{page.page_num}_table_{index + 1}.png")
                table_data = self._gather_table_metadata(table, table_img_path, page.page_num)
                self.extracted_tables.append(table_data)

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
