21 document_analyzer.extract_figures()     24 document_analyzer.extract_tables()---> 26 text=document_analyzer.extract_raw_text()     29 print("Extracted Figures:", document_analyzer.extracted_figures)     30 print("Extracted Tables:", document_analyzer.extracted_tables) Cell In[46], line 64     62 for page in self.document.pages:     63     print("------page in the document is",page)---> 64     self._process_page_for_text(page) Cell In[46], line 74     70     print("------layout in the document is",layout)     71     if layout.layout_type not in ['LAYOUT_FIGURE', 'LAYOUT_TABLE']:     72         layout_data = {     73             "layout_id": layout.id,---> 74             "layout_name": f'page_{page.page}_layout_{index}',     75             "layout_reading_order": layout.reading_order,     76             "layout_type": layout.layout_type,     77             "layout_text": layout.text,     78             "layout_confidence": layout.confidence,     79             "layout_width": layout.width,
...
     90     "page_full_text": page_full_text,     91     "text_layout_data": text_layouts_extracted     92 } AttributeError: 'Page' object has no attribute 'page'
has context menu
