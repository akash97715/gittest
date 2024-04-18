import os
import logging
import aiofiles
import asyncio

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DocumentAnalyzer:
    def __init__(self, extractor, file_source, doc_name, s3_upload_path):
        self.extractor = extractor
        self.file_source = file_source
        self.doc_name = doc_name
        self.s3_upload_path = s3_upload_path
        self.extracted_figures = []
        self.extracted_tables = []

    async def start_analysis(self, features):
        try:
            # Assuming `start_document_analysis` is an async method
            return await self.extractor.start_document_analysis(file_source=self.file_source,
                                                                s3_upload_path=self.s3_upload_path,
                                                                features=features)
        except Exception as e:
            logging.error("Failed to start document analysis: %s", e)
            raise

    async def extract_figures(self):
        try:
            document = await self.start_analysis([TextractFeatures.LAYOUT, TextractFeatures.TABLES])
            tasks = [self._process_page_for_figures(page) for page in document.pages]
            await asyncio.gather(*tasks)
        except Exception as e:
            logging.error("Failed to extract figures: %s", e)

    async def _process_page_for_figures(self, page):
        try:
            figures_in_page = [layout for layout in page.layouts if layout.layout_type == 'LAYOUT_FIGURE']
            for index, figure in enumerate(figures_in_page):
                cropped_img = self._crop_image(page.image, figure.bbox, page.image.size)
                figure_path = await self._save_cropped_image(cropped_img, "figures", f"page_{page.page_num}_figure_{index + 1}.png")
                figure_info = self._gather_figure_metadata(figure, figure_path, page.page_num)
                self.extracted_figures.append(figure_info)
        except Exception as e:
            logging.error("Failed to process page for figures: %s", e)

    async def extract_tables(self):
        try:
            document = await self.start_analysis([TextractFeatures.TABLES])
            tasks = [self._process_page_for_tables(page) for page in document.pages]
            await asyncio.gather(*tasks)
        except Exception as e:
            logging.error("Failed to extract tables: %s", e)

    async def _process_page_for_tables(self, page):
        try:
            if page.tables:
                for index, table in enumerate(page.tables):
                    cropped_img = self._crop_image(page.image, table.bbox, page.image.size)
                    table_img_path = await self._save_cropped_image(cropped_img, "tables/img", f"page_{page.page_num}_table_{index + 1}.png")
                    table_data = self._gather_table_metadata(table, table_img_path, page.page_num)
                    self.extracted_tables.append(table_data)
        except Exception as e:
            logging.error("Failed to process page for tables: %s", e)

    def _crop_image(self, image, bbox, size):
        x, y, width, height = bbox.x * size[0], bbox.y * size[1], bbox.width * size[0], bbox.height * size[1]
        return image.crop((x, y, x + width, y + height))

    async def _save_cropped_image(self, image, subdir, filename):
        try:
            path = os.path.join(self.doc_name, subdir)
            if not os.path.exists(path):
                os.makedirs(path)
            image_path = os.path.join(path, filename)
            async with aiofiles.open(image_path, 'wb') as f:
                await f.write(image.tobytes())  # Assuming image.tobytes() gives the byte-like object needed
            return image_path
        except Exception as e:
            logging.error("Failed to save cropped image: %s", e)
            raise

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

# Usage of this class requires an asynchronous context
