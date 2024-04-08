from typing import Iterator, List
import textractor.entities.document as textractor_document

class EnhancedTextractLoader:
    def __init__(self, loader):
        """
        Initialize with an instance of AmazonTextractPDFLoader.
        """
        self.loader = loader

    def load_and_parse(self) -> List[dict]:
        """
        Load the document using the loader and parse it to extract tables, images, and text.
        """
        documents = self.loader.load()  # Use the base loader to load documents
        enhanced_documents = [self.enhance_document_with_features(doc) for doc in documents]
        return enhanced_documents

    def enhance_document_with_features(self, document: textractor_document.Document) -> dict:
        """
        Enhance a single document with tables, images, and text extracted from the Textract response.
        """
        # Initialize containers for enhanced features
        tables = []
        images = []
        text_lines = []

        # Assuming the 'document' is a parsed Textract document
        for page in document.pages:
            for block in page.blocks:
                if block.block_type == 'TABLE':
                    tables.append(self._process_table_block(block))
                elif block.block_type == 'LINE':
                    text_lines.append(block.text)
                elif block.block_type == 'IMAGE':
                    images.append(self._process_image_block(block))

        # Construct an enhanced document structure
        enhanced_document = {
            'page_content': '\n'.join(text_lines),
            'metadata': {
                'tables': tables,
                'images': images
            }
        }
        return enhanced_document

    def _process_table_block(self, block) -> dict:
        """
        Process a table block to extract table data.
        """
        # Example implementation, adapt based on actual block structure
        table_data = {'rows': []}
        for relationship in block.relationships:
            if relationship.type == 'CHILD':
                for child_id in relationship.ids:
                    cell = self._find_block_by_id(child_id, block.page.blocks)
                    if cell and cell.block_type == 'CELL':
                        row_index = cell.row_index - 1
                        col_index = cell.column_index - 1
                        # Ensure row exists
                        while len(table_data['rows']) <= row_index:
                            table_data['rows'].append([])
                        # Ensure cell exists in row
                        row = table_data['rows'][row_index]
                        while len(row) <= col_index:
                            row.append(None)
                        # Set cell value
                        row[col_index] = cell.text
        return table_data

    def _process_image_block(self, block) -> dict:
        """
        Process an image block to extract image data.
        """
        # Example implementation, adapt based on actual block structure
        return {
            'geometry': block.geometry
        }

    def _find_block_by_id(self, block_id, blocks) -> dict:
        """
        Find a block by its ID within the given list of blocks.
        """
        for block in blocks:
            if block.id == block_id:
                return block
        return None





from langchain_community.document_loaders import AmazonTextractPDFLoader
from textractor.data.text_linearization_config import TextLinearizationConfig
# Assuming EnhancedTextractLoader is the class we discussed earlier

# Step 3: Initialize AmazonTextractPDFLoader with your document's path
document_path = "s3://your-bucket/path-to-your-document.pdf"  # Example S3 URI
loader = AmazonTextractPDFLoader(
    file_path=document_path,
    textract_features=["TABLES", "FORMS"],  # Specify features as needed
    region_name="us-east-1",  # Example AWS region
    # Add any other necessary parameters
    linearization_config=TextLinearizationConfig(
        hide_header_layout=True,
        hide_footer_layout=True,
        hide_figure_layout=True,
    ),
)

# Step 4: Use EnhancedTextractLoader
enhanced_loader = EnhancedTextractLoader(loader)
enhanced_documents = enhanced_loader.load_and_parse()

# Now `enhanced_documents` contains your processed documents
