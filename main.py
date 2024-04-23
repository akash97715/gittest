import os
import logging
import base64
import uuid
from PIL import Image

class CustomTextractor:
    def __init__(self, file_source, doc_name, s3_upload_path, filename):
        self.file_source = file_source
        self.filename = filename
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

        first_filter_pass_tables = []
        final_filter_pass_tables = []

        for page in self.document.pages:
            for index, table in enumerate(page.tables):
                table_verification_layouts_types = [layout.layout_type for layout in page.layouts if layout.layout_type in ['LAYOUT_TABLE']]
                confidence = table.raw_object['Confidence']
                
                # Stage 1: Initial filtering based on layout type and confidence
                if len(table_verification_layouts_types) == 1 or ('LAYOUT_TABLE' in table_verification_layouts_types and confidence > 90):
                    if confidence > 95:
                        final_filter_pass_tables.append(table)
                    else:
                        first_filter_pass_tables.append(table)

        # Process tables that passed final filtering
        for table in final_filter_pass_tables:
            self._process_table(table, page)

        # Process tables that only passed the first stage of filtering
        for table in first_filter_pass_tables:
            cropped_img = self._crop_image(page.image, table.bbox, page.image.size)
            table_img_path = self._save_cropped_image(cropped_img, "img", f"page_{page.page_num}_table_{index + 1}.jpg")
            # Optionally gather and store metadata for these images if needed

    def _process_table(self, table, page):
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
                    "layout_name": f'page_{page.page_num}_layout_{index}',
                    "layout_reading_order": layout.reading_order,
                    "layout_type": layout.layout_type,
                    "layout_text": layout.text,
                    "layout_confidence": layout.confidence,
                    "layout_width": layout.width,
                    "layout_height": layout.height,
                    "layout_x": layout.x,
                    "layout_y": layout.y,
                    "layout_page": page.page_num,
                }
                text_layouts_extracted.append(layout_data)

        page_text_layout = {
            "document_name": self.doc_name,
            "page_num": page.page_num,
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
    # Additional methods for encoding, ingesting images and tables, and custom text extraction would be included here as well.
