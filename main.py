def ingest_image(self,path_to_ingest="/figures"):
       
       
        if path_to_ingest=='/figures':
            path = os.path.join(self.doc_name, 'figures')
            final_image_list=os.listdir(self.doc_name+path_to_ingest)
            print("FINAL IMAGE LIST",final_image_list)
        else:
            path = os.path.join(self.doc_name, 'tables/img')
            print("ITS COMING TO table  image path")
            all_list=os.listdir(self.doc_name+path_to_ingest)
            print("ALL THE TABLES",all_list)
            table_not_be_considered=[i['figure_name'] for i in self.final_table]
            print("TABLE NOT TO BE CONSIDERED",table_not_be_considered)
            final_image_list=[i for i in all_list if i not in table_not_be_considered]
            print("FINAL_TABLE_LIST",final_image_list)
 
           
        print("its coming here or not",path)
 
        # Check if the path exists
        if not os.path.exists(path):
            print("terminating--------------------------------------",path)
            return [], []
        print("its coming here or not--------------------------------------",path)
 
        img_base64_list = []
        image_summaries = []
        path_to_consider=self.extracted_figures if path_to_ingest =='/figures' else self.extracted_tables
 
        img_ids = [
            "{}/{}/{}".format(self.client_id, self.index_name, uuid.uuid4())
            for _ in final_image_list
        ]
        details_map = {item["figure_name"]: item for item in path_to_consider}
        metadata_dict = self.additional_metadata
        print("FINAL MAGE LIST",details_map)
 
        # Iterate over the sorted list of files in the directory
        for img_file in sorted(os.listdir(path)):
            if img_file.endswith(".jpg") and img_file in final_image_list:
                img_path = os.path.join(path, img_file)
 
                base64_image = self.encode_image(img_path)
                img_base64_list.append(base64_image)
                if img_file in details_map:
                    details = details_map[img_file]
                    page_content = f"{self.filename} {details['figure_name']} page {details['figure_page']}"
                    metadata = {
                        **metadata_dict,
                        "id_key": img_ids[sorted(os.listdir(path)).index(img_file)],
                        "document_name": self.filename,
                        "figure_name": details["figure_name"],
                    }
                    image_summaries.append(
                        Document(page_content=page_content, metadata=metadata)
                    )
 
        self.memory_store.mmset(list(zip(img_ids, img_base64_list)))
 
        return image_summaries, img_ids
