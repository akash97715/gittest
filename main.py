import os
import uuid

class ImageIngestor:
    def __init__(self, doc_name, extracted_figures, filename):
        self.doc_name = doc_name
        self.extracted_figures = extracted_figures
        self.filename = filename

    def ingest_image(self):
        path = os.path.join(self.doc_name, 'figures')

        # Check if the path exists
        if not os.path.exists(path):
            print(f"No figures directory found at {path}")
            return [], []

        img_base64_list = []
        image_summaries = []
        img_ids = [str(uuid.uuid4()) for _ in self.extracted_figures]
        details_map = {item['figure_name']: item for item in self.extracted_figures}

        # Iterate over the sorted list of files in the directory
        for img_file in sorted(os.listdir(path)):
            print(f"=========the path for image extraction: {img_file}")
            if img_file.endswith('.jpg'):
                img_path = os.path.join(path, img_file)
                print(f"=========the path for image extraction: {img_path}")
                base64_image = self.encode_image(img_path)
                img_base64_list.append(base64_image)
                if img_file in details_map:
                    details = details_map[img_file]
                    page_content = f"{self.filename} {details['figure_name']} page {details['figure_page']}"
                    metadata = {
                        "id_key": img_ids[sorted(os.listdir(path)).index(img_file)],
                        "document_name": self.filename,
                        "figure_name": details['figure_name']
                    }
                    image_summaries.append(Document(page_content=page_content, metadata=metadata))

        # Store in a hypothetical S3 document store
        memory_store = S3DocStore(DOC_STORE_BUCKET)
        memory_store.mset(list(zip(img_ids, img_base64_list)))

        return image_summaries, img_ids

    def encode_image(self, img_path):
        # This method should encode the image to base64
        pass

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

class S3DocStore:
    def __init__(self, bucket):
        self.bucket = bucket

    def mset(self, data):
        # This method should store the data in S3
        pass
