def custom_extraction(self):
        import io
        import os
        import base64
        import numpy as np
        from PIL import Image        
 
        #create raw_text conetent that need to be ingested
        parent_documents, (page_content, metadata, large_file)=self.process_files()
 
 
        image_embedding_content=self.extracted_figures
        ghg_table=self.extracted_tables
        img_ids = [str(uuid.uuid4()) for _ in img_base64_list]
               
 
 
       
        html_content_list = [table['table_html'] for table in ghg_table]
        #table_ingestionprep
        metadata_dict = {'doc_name': 'something', 'doc_md5': '14516542652'}
        table_ids = [str(uuid.uuid4()) for _ in ghg_table]
        summary_table=[
            Document(
                page_content=f"{item['document_name']} {item.get('table_page_number', '')} {item.get('table_title', '')} {' '.join(item.get('footers', []))}".strip(),
                metadata={
                    **metadata_dict,
                   
                    'page_number': item.get('table_page_number', ''),
                    'id_key': table_ids[index]  # Assigning UUID from the generated list
                }
            )
            for index, item in enumerate(ghg_table)
        ]
        img_base64_list = []
       
        # Store image summaries
        image_summaries = []
       
        # Create a mapping of figure names to document details
        details_map = {item['figure_name']: item for item in image_embedding_content}
        img_ids = [str(uuid.uuid4()) for _ in image_embedding_content]
       
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
                    document = Document(page_content=page_content, metadata=metadata)
                    image_summaries.append(document)
        retriever.vectorstore.add_documents(summary_table)
        retriever.docstore.mset(list(zip(table_ids, html_content_list)))
        retriever.vectorstore.add_documents(image_summaries)
        retriever.docstore.mset(list(zip(img_ids, img_base64_list)))        
        final_rds_metadata={}
        final_rds_metadata['image']=img_ids
        final_rds_metadata['table']=table_ids
