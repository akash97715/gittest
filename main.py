import os
import base64

path = "tobeingest/figures"

# Define the Document class
class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

def encode_image(image_path):
    ''' Getting the base64 string '''
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Store base64 encoded images
img_base64_list = []

# Store image summaries
image_summaries = []

# Create a mapping of figure names to document details
details_map = {item['figure_name']: item for item in payload}

# Assuming img_ids is defined or populated somewhere above
img_ids = [item['figure_id'] for item in payload]

for i, img_file in enumerate(sorted(os.listdir(path))):
    if img_file.endswith('.jpg'):
        img_path = os.path.join(path, img_file)
        base64_image = encode_image(img_path)
        img_base64_list.append(base64_image)
        
        # Retrieve details from the map using filename
        if img_file in details_map:
            details = details_map[img_file]
            page_content = f"{details['document_name']} {details['figure_name']} page {details['figure_page']}"
            metadata = {
                "id_key": img_ids[i],  # Here we use the corresponding img_id
                "document_name": details['document_name'],
                "figure_name": details['figure_name']
            }
            document = Document(page_content, metadata)
            image_summaries.append(document)
