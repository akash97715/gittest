def process_table(self, table, page):
       
        cropped_image = self._crop_image(page.image, table.bbox, page.image.size)
        table_img_path = self._save_cropped_image(
            cropped_image, "tables/img", f"page_{page.page_num}_table.jpg"
        )
       
        table_data = self._gather_table_metadata(table, table_img_path, page.page_num)
        table_info = self._gather_table_metadata(table, table_img_path, page.page_num)
 
        #table_info = self.collect_table_info(table, table_name, table_img_path)
        self.extracted_tables.append(table_info)
 
        # Verify table layout by analyzing the cropped table image
        if self.advance_table_filter:
            self.verify_table_layout(cropped_image, table_info)
