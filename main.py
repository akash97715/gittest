        if self.advance_table_filter:
            await self._verify_table_layout(cropped_image, table_info)
        else:
            print("TABLE INFORMATION===========================================",table_info)
           
            self.extracted_tables.append(table_info)
