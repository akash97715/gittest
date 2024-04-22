document_text_layout = []
 
# for every page extract text layouts with relevant metadata plus full page text
for page in layout_analysis_doc_object.pages:
 
    page_full_text = page.text  # will return also texted included in fugures and tables
 
    text_layouts_extracted = []
 
    for index, layout in enumerate(page.layouts):
        if layout.layout_type != 'LAYOUT_FIGURE' and layout.layout_type != 'LAYOUT_TABLE':
            layout_name = f'page_{layout.page}_layout_{index}'
            layout_id = layout.id
            layout_reading_order = layout.reading_order
            layout_type = layout.layout_type
            layout_text = layout.text
            layout_conf = layout.confidence
            layout_width = layout.width
            layout_height = layout.height
            layout_x = layout.x
            layout_y = layout.y
 
            layout_data = {
                    "layout_id": layout_id,
                    "layout_name": layout_name,
                    "layout_reading_order": layout_reading_order,
                    "layout_type": layout_type,
                    "layout_text": layout_text,
                    "layout_confidence": layout_conf,
                    "layout_width": layout_width,
                    'layout_height': layout_height,
                    'layout_x': layout_x,
                    'layout_y': layout_y,
                    'layout_page': layout.page,
                }
 
        text_layouts_extracted.append(layout_data)
 
    page_text_layout = {
        "document_name": doc_name,
        "page_num": page.page_num,
        "page_full_text": page_full_text,
        "text_layout_data": text_layouts_extracted
    }
 
    document_text_layout.append(page_text_layout)
