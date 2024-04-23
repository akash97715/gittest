import os
import logging
from textractor import Textractor
from textractor.data.constants import TextractFeatures

class DocumentAnalyzer:
    def __init__(self, file_source, doc_name, s3_upload_path):
        self.file_source = file_source
        self.doc_name = doc_name
        self.s3_upload_path = s3_upload_path
        self.extracted_figures = []
        self.extracted_tables = []
        self.document_text_layouts = []
        self.textractor = Textractor(profile_name="default")
        self.document = None  # Hold the analyzed document
 
    def start_analysis(self):
        try:
            print("===============================file sent for analysis", self.file_source)
            self.document = self.textractor.start_document_analysis(
                file_source=self.file_source,
                s3_upload_path=self.s3_upload_path,
                features=[TextractFeatures.LAYOUT, TextractFeatures.TABLES]
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
            self._process_page_for_text(page)

    def _process_page_for_text(self, page):
        page_full_text = page.text
        text_layouts_extracted = []

        for index, layout in enumerate(page.layouts):
            if layout.layout_type not in ['LAYOUT_FIGURE', 'LAYOUT_TABLE']:
                layout_data = {
                    "layout_id": layout.id,
                    "layout_name": f'page_{layout.page}_layout_{index}',
                    "layout_reading_order": layout.reading_order,
                    "layout_type": layout.layout_type,
                    "layout_text": layout.text,
                    "layout_confidence": layout.confidence,
                    "layout_width": layout.width,
                    "layout_height": layout.height,
                    "layout_x": layout.x,
                    "layout_y": layout.y,
                    "layout_page": layout.page,
                }
                text_layouts_extracted.append(layout_data)

        page_text_layout = {
            "document_name": self.doc_name,
            "page_num": page.page_num,
            "page_full_text": page_full_text,
            "text_layout_data": text_layouts_extracted
        }

        self.document_text_layouts.append(page_text_layout)

