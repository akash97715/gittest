[12:39 PM] Deep, Akash (External)
    async def load(self):
 
        try:
            features = [TextractFeatures.LAYOUT, TextractFeatures.TABLES]
            self.document = self.textractor.start_document_analysis(
                file_source=self.file_source,
                s3_upload_path=self.s3_upload_path,
                features=features,
            )
            total_pages=len(PyPDF2.PdfReader(self.filename).pages)
            extra_image_summary=[]
            extra_image_uuid=[]            
            self.extract_figures()
            self.extract_tables()
            self.extract_raw_text()
            image_summary, image_uuid = await self.ingest_image()
            table_summary, table_uuid = await self.ingest_tables()
            if self.advance_table_filter:
               
                extra_image_summary, extra_image_uuid= await self.ingest_image(path_to_ingest="/tables/img")
            raw_pages = self._custom_textract_text_loader()
           
               
        except Exception as e:
            error_type = e.__class__.__name__.replace("Error", "")
            logging.error(f"Error during {error_type.lower()} process", exc_info=True)
            raise CustomTextractException(error_type, e)
        adv_atble_filter=True if self.advance_table_filter else False
        meteringdata={'totalPages':total_pages,'totalTable':len(self.extracted_tables),'advTableFilter':adv_atble_filter}
        final_rds_metadata = {"images": image_uuid, "tables": table_uuid,"extra_image_uuid":extra_image_uuid,"metering_data":meteringdata}
        return image_summary, table_summary, raw_pages, final_rds_metadata,extra_image_summary
[12:39 PM] Deep, Akash (External)
    async def ingest_image(self, path_to_ingest="/figures"):
        # Determine the correct path based on the input parameter
        if path_to_ingest == '/figures':
            path = os.path.join(self.doc_name, 'figures')
        else:
            path = os.path.join(self.doc_name, 'tables', 'img')
   
        # Check if the path exists
        if not os.path.exists(path):
           
            return [], []
   
        # List all files in the path
        files_in_path = os.listdir(path)
       
   
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
                        "type":"image",
                        "figure_name": details["figure_name"],
                    }
                    image_summaries.append(Document(page_content=page_content, metadata=metadata))
        asyncio.run(self.memory_store.mset(list(zip(img_ids, img_base64_list))))
   
        #await self.memory_store.mset(list(zip(img_ids, img_base64_list)))
   
        return image_summaries, img_ids
