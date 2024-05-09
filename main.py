if self.advance_table_filter:
    await self._verify_table_layout(cropped_image, table_info)
else:
    higher, lower = sum((self.extracted_tables.append(info), 1)[1] if info['table_confidence'] > self.table_threshold_score else (self.extracted_figures.append(info), 0)[1] for info in doclist), len(doclist) - sum(info['table_confidence'] > self.table_threshold_score for info in doclist)
    print(f"Processed TABLE INFORMATION: {higher} tables higher than threshold, {lower} tables lower than threshold")
