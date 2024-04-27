def process_table(self, table, page):
    # Assuming there's an attribute to keep count of tables per page
    if not hasattr(self, 'table_count'):
        self.table_count = {}
    
    # Initialize or increment the table counter for the current page
    if page.page_num not in self.table_count:
        self.table_count[page.page_num] = 0
    else:
        self.table_count[page.page_num] += 1

    # Use the page number and the current table count for the dynamic part of the file name
    dynamic_part = f"page_{page.page_num}_table_{self.table_count[page.page_num]}"
    
    cropped_image = self._crop_image(page.image, table.bbox, page.image.size)
    table_img_path = self._save_cropped_image(
        cropped_image, "tables/img", f"{dynamic_part}.jpg"
    )

    table_data = self._gather_table_metadata(table, table_img_path, page.page_num)
    table_info = self._gather_table_metadata(table, table_img_path, page.page_num)

    self.extracted_tables.append(table_info)

    # Verify table layout by analyzing the cropped table image
    if self.advance_table_filter:
        self.verify_table_layout(cropped_image, table_info)
