import os
from PIL import Image

class DocumentAnalyzer:
    def __init__(self, extractor, doc_name, s3_upload_path):
        self.extractor = extractor
        self.doc_name = doc_name
        self.s3_upload_path = s3_upload_path
        self.figures = []
        self.tables = []
        self.final_tables = []
        self.setup_directories()

    def setup_directories(self):
        os.makedirs(f"{self.doc_name}/figures", exist_ok=True)
        os.makedirs(f"{self.doc_name}/tables/img", exist_ok=True)

    def analyze_document(self, features):
        return self.extractor.start_document_analysis(
            f"Docs/{self.doc_name}", s3_upload_path=self.s3_upload_path, features=features)

    def extract_figures(self, doc_object):
        for page in doc_object.pages:
            for layout in page.layouts:
                if layout.layout_type == 'LAYOUT_FIGURE':
                    self.process_figure(layout, page)

    def process_figure(self, layout, page):
        figure_name = f'page_{page.page_num}_figure_{len(self.figures) + 1}'
        cropped_image = self.crop_image(page.image, layout.bbox, page.image.size)
        figure_path = f'{self.doc_name}/figures/{figure_name}.png'
        cropped_image.save(figure_path)

        figure_info = {
            "document_name": self.doc_name,
            "figure_id": layout.id,
            "figure_name": figure_name,
            "figure_page": page.page_num,
            "figure_confidence": layout.confidence,
            "figure_bbox": layout.bbox,
            "figure_path": figure_path
        }
        self.figures.append(figure_info)

    def extract_tables(self, doc_object):
        for page in doc_object.pages:
            for table in page.tables:
                self.process_table(table, page)

    def process_table(self, table, page):
        table_name = f'page_{page.page_num}_table_{len(self.tables) + 1}'
        cropped_image = self.crop_image(page.image, table.bbox, page.image.size)
        table_img_path = f'{self.doc_name}/tables/img/{table_name}.png'
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

    def validate_tables(self, table_info):
        layouts = table_info['verification_layouts']
        if len(layouts) == 1 or any(l['type'] == 'LAYOUT_TABLE' and l['confidence'] > 90 for l in layouts):
            if table_info['table_confidence'] > 95:
                self.final_tables.append(table_info)

    def crop_image(self, image, bbox, size):
        page_width, page_height = size
        area = (
            bbox.x * page_width, bbox.y * page_height,
            (bbox.x + bbox.width) * page_width, (bbox.y + bbox.height) * page_height
        )
        return image.crop(area)

    def collect_table_info(self, table, table_name, table_img_path):
        return {
            "document_name": self.doc_name,
            "table_id": table.id,
            "table_name": table_name,
            "table_bbox": table.bbox,
            "table_column_count": table.column_count,
            "table_confidence": table.raw_object['Confidence'],
            "table_img_path": table_img_path,
            "column_headers": [cell.text for cell in table.table_cells if cell.is_column_header],
            "footers": [footer.text for footer in table.footers],
            "table_html": table.to_html(),
            "table_markdown": table.to_markdown(),
        }

# Usage example:
extractor = TextractWrapper()  # Assume TextractWrapper is the API wrapper for AWS Textract
doc_analyzer = DocumentAnalyzer(extractor, "example_document", "s3_bucket_path")
tables_doc = doc_analyzer.analyze_document([TextractFeatures.TABLES])
figures_doc = doc_analyzer.analyze_document([TextractFeatures.LAYOUT])

doc_analyzer.extract_figures(figures_doc)
doc_analyzer.extract_tables(tables_doc)
