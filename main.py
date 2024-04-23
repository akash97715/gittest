import os
import base64

path = "tobeingest/figures"

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

for img_file in sorted(os.listdir(path)):
    if img_file.endswith('.jpg'):
        img_path = os.path.join(path, img_file)
        base64_image = encode_image(img_path)
        img_base64_list.append(base64_image)
        
        # Retrieve details from the map using filename
        if img_file in details_map:
            details = details_map[img_file]
            summary = f"{details['document_name']} {details['figure_name']} page {details['figure_page']}"
            image_summaries.append(summary)
