import os
import uuid

def ingest_image(self, path_to_ingest="/figures"):
    # Determine the correct path based on the input parameter
    if path_to_ingest == '/figures':
        path = os.path.join(self.doc_name, 'figures')
    else:
        path = os.path.join(self.doc_name, 'tables', 'img')

    # Check if the path exists
    if not os.path.exists(path):
        print("Path does not exist:", path)
        return [], []

    # List all files in the path
    files_in_path = os.listdir(path)
    print("Files in path:", files_in_path)

    # Filter the files based on specific conditions
    if path_to_ingest == '/figures':
        final_image_list = files_in_path
    else:
        # Extract figure names not to be considered
        table_not_be_considered = [i['figure_name'] for i in self.final_table]
        # Filter the extracted tables to exclude those listed in table_not_be_considered
        final_image_list = [i for i in files_in_path if i not in table_not_be_considered]
        # Additionally, filter the extracted tables details
        filtered_table_details = [item for item in self.extracted_tables if item['figure_name'] not in table_not_be_considered]

    print("Final image list:", final_image_list)

    img_base64_list = []
    image_summaries = []
    img_ids = ["{}/{}/{}".format(self.client_id, self.index_name, uuid.uuid4()) for _ in final_image_list]
    details_map = {item["figure_name"]: item for item in filtered_table_details} if path_to_ingest != '/figures' else {item["figure_name"]: item for item in self.extracted_figures}

    # Iterate over the sorted list of files that are relevant
    for img_file in sorted(final_image_list):
        if img_file.endswith(".jpg"):
            img_path = os.path.join(path, img_file)

            base64_image = self.encode_image(img_path)
            img_base64_list.append(base64_image)

            if img_file in details_map:
                details = details_map[img_file]
                page_content = f"{self.filename} {details['figure_name']} page {details['figure_page']}"
                metadata = {
                    **self.additional_metadata,
                    "id_key": img_ids[sorted(final_image_list).index(img_file)],
                    "document_name": self.filename,
                    "figure_name": details["figure_name"],
                }
                image_summaries.append(Document(page_content=page_content, metadata=metadata))

    self.memory_store.mmset(list(zip(img_ids, img_base64_list)))

    return image_summaries, img_ids
