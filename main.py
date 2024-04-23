def _process_page_for_text(self, page):
    page_full_text = page.text
    text_layouts_extracted = []

    for index, layout in enumerate(page.layouts):
        if layout.layout_type not in ['LAYOUT_FIGURE', 'LAYOUT_TABLE']:
            layout_data = {
                "layout_id": layout.id,
                "layout_name": f'page_{page.page_num}_layout_{index}',  # Adjusted to use the correct page number attribute
                "layout_reading_order": layout.reading_order,
                "layout_type": layout.layout_type,
                "layout_text": layout.text,
                "layout_confidence": layout.confidence,
                "layout_width": layout.width,
                "layout_height": layout.height,
                "layout_x": layout.x,
                "layout_y": layout.y,
                "layout_page": page.page_num,  # Ensuring correct page number is referenced
            }
            text_layouts_extracted.append(layout_data)

    page_text_layout = {
        "document_name": self.doc_name,
        "page_num": page.page_num,  # Corrected
        "page_full_text": page_full_text,
        "text_layout_data": text_layouts_extracted
    }

    self.document_text_layouts.append(page_text_layout)
