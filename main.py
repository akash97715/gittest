if self.advance_table_filter:
    await self._verify_table_layout(cropped_image, table_info)
else:
    [self.extracted_tables.append(info) if info['table_confidence'] > self.table_threshold_score else self.extracted_figures.append(info) for info in doclist]
    print("Processed TABLE INFORMATION")
