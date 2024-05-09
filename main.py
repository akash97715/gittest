if self.advance_table_filter:
    await self._verify_table_layout(cropped_image, table_info)
else:
    action = (self.extracted_tables.append(doclist), "higher")[1] if doclist['table_confidence'] > self.table_threshold_score else (self.extracted_figures.append(doclist), "lower")[1]
    print(f"Processed TABLE INFORMATION: 1 table {action} than threshold")
