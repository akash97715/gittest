    def ingest_image(self):
        img_base64_list = []
        image_summaries = []
        img_ids = [str(uuid.uuid4()) for _ in self.extracted_figures]
        details_map = {item['figure_name']: item for item in self.extracted_figures}
        path=self.doc_name+'/figures'
 
       
 
        # Assuming 'path' is defined globally or within the class
        for img_file in sorted(os.listdir(path)):
            print("=========the path for image extraction",img_file)
            if img_file.endswith('.jpg'):
                img_path = os.path.join(path, img_file)
                print("=========the path for image extraction",img_path)
                base64_image = self.encode_image(img_path)
                img_base64_list.append(base64_image)
                if img_file in details_map:
                    details = details_map[img_file]
                    page_content = f"{self.filename} {details['figure_name']} page {details['figure_page']}"
                    metadata = {
                        "id_key": img_ids[sorted(os.listdir(path)).index(img_file)],  # Use sorted index
                        "document_name": self.filename,
                        "figure_name": details['figure_name']
                    }
                    image_summaries.append(Document(page_content=page_content, metadata=metadata))
        memory_store = S3DocStore(DOC_STORE_BUCKET)
        memory_store.mset(list(zip(img_ids, img_base64_list)))
 
 
        return image_summaries, img_ids
