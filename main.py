import io
import os
import base64
import uuid
import numpy as np
from PIL import Image

class MyClass:
    def encode_image(self, img_path):
        with Image.open(img_path) as img:
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def custom_extraction(self):
        # Assumes process_files and other relevant methods are defined within the class
        parent_documents, (page_content, metadata, large_file) = self.process_files()

        image_embedding_content = self.extracted_figures
        ghg_table = self.extracted_tables
        
        # Generate UUIDs for tables and images
        table_ids = [str(uuid.uuid4()) for _ in ghg_table]
        img_ids = [str(uuid.uuid4()) for _ in image_embedding_content]
        
        # Preparing metadata dict outside the loop for efficiency
        metadata_dict = {'doc_name': 'something', 'doc_md5': '14516542652'}
        
        # Summary table preparation
        summary_table = [
            Document(
                page_content=f"{item['document_name']} {item.get('table_page_number', '')} {item.get('table_title', '')} {' '.join(item.get('footers', []))}".strip(),
                metadata={
                    **metadata_dict,
                    'page_number': item.get('table_page_number', ''),
                    'id_key': table_ids[index]
                }
            )
            for index, item in enumerate(ghg_table)
        ]

        # HTML content extraction for tables
        html_content_list = [table['table_html'] for table in ghg_table]
        
        # Image handling
        img_base64_list = []
        image_summaries = []
        details_map = {item['figure_name']: item for item in image_embedding_content}

        # Assuming 'path' is defined globally or within the class
        for img_file in sorted(os.listdir(self.path)):
            if img_file.endswith('.jpg'):
                img_path = os.path.join(self.path, img_file)
                base64_image = self.encode_image(img_path)
                img_base64_list.append(base64_image)
                
                if img_file in details_map:
                    details = details_map[img_file]
                    page_content = f"{details['document_name']} {details['figure_name']} page {details['figure_page']}"
                    metadata = {
                        "id_key": img_ids[sorted(os.listdir(self.path)).index(img_file)],  # Use sorted index
                        "document_name": details['document_name'],
                        "figure_name": details['figure_name']
                    }
                    image_summaries.append(Document(page_content=page_content, metadata=metadata))

        # Assuming retriever is an initialized object within the class
        self.retriever.vectorstore.add_documents(summary_table)
        self.retriever.docstore.mset(list(zip(table_ids, html_content_list)))
        self.retriever.vectorstore.add_documents(image_summaries)
        self.retriever.docstore.mset(list(zip(img_ids, img_base64_list)))

        final_rds_metadata = {'image': img_ids, 'table': table_ids}
        return final_rds_metadata

# Assuming Document is properly defined elsewhere in your codebase
