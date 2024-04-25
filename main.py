%%time
tables_analysis_doc_object = extractor.start_document_analysis(f"Docs/{doc_name}",
                                                  s3_upload_path=s3_upload_path,
                                              features=[TextractFeatures.TABLES])
 
%%time
layout_analysis_doc_object = extractor.start_document_analysis(file_source=f"Docs/{doc_name}",
                                                  s3_upload_path=s3_upload_path,
                                              features=[TextractFeatures.LAYOUT])
 
# Create empty list to store figure information
extracted_figures_list = []
 
# for every page
for page in layout_analysis_doc_object.pages:
 
    page_num = page.page_num
    page_image = page.image
    page_width, page_height = page_image.size
 
    layout_figures_in_page = []
 
    for layout in page.layouts:
        if layout.layout_type == 'LAYOUT_FIGURE':
            layout_figures_in_page.append(layout)
 
    # check if page has one or more layouts
    if layout_figures_in_page:
 
        # for every figure in page get information
        for index, figure in enumerate(layout_figures_in_page):
 
            # get the page of the figure
            figure_page = figure.page
 
            # create a name figure
 
            figure_name = f'page_{page_num}_figure_{index + 1}'
 
            # figure bbox
            figure_bbox = figure.bbox
 
            # specify area to crop
            area_to_crop = (
                figure_bbox.x * page_width,
                figure_bbox.y * page_height,
                (figure_bbox.x + figure_bbox.width) * page_width,
                (figure_bbox.y + figure_bbox.height) * page_height
            )
 
            # crop page image based on figure area
            page_img_cropped = page_image.crop(area_to_crop)
 
            # create a folder for the documnt to store the figures if it doesn't exist:
            if not os.path.exists(f"{doc_name}/figures"):
                os.makedirs(f"{doc_name}/figures")
 
            figure_path = f'{doc_name}/figures/{figure_name}.png'
            # save the figure in a png file
            page_img_cropped.save(figure_path)
 
            # gather all figure metadata needed
            figure_info = {
                "document_name": doc_name,
                "figure_id": figure.id,
                "figure_name": figure_name,
                "figure_page": figure_page,
                "figure_confidence": figure.confidence,
                "figure_bbox": figure_bbox,
                "figure_height": figure.height,
                "figure_width": figure.width,
                "figure_x": figure.x,
                "figure_y": figure.y,
                "figure_path": figure_path
            }
 
            extracted_figures_list.append(figure_info)
 
%%time
extracted_initial_table_list = []
 
# for every page
for page in tables_analysis_doc_object.pages:
    print('run loop 1')
    page_num = page.page_num
    page_image = page.image
    page_width, page_height = page_image.size
 
    # check if page has one or more tables
    if page.tables:
        for index, table in enumerate(page.tables):
            table_name = f'page_{page_num}_table_{index + 1}'
            print('run loop 2')
 
            # get table metadata
            table_id = table.id
            table_bbox = table.bbox
            table_column_count = table.column_count
            # get table footers
            footers = []
            for footer in table.footers:
                print('run loop 3')
                footers.append(footer.text)
            table_height = table.height
            table_metadata = table.metadata
            table_page_number = table.page
            table_page_id = table.page_id
            table_confidence = table.raw_object['Confidence']
            table_row_count = table.row_count
            table_cells_info = table.table_cells
            # get table column headers
            column_headers = []
            for cell in table_cells_info:
                print('run loop 4')
                if cell.is_column_header:
                    column_headers.append(cell.text)
            # for column_headers in table.column_headers:
            #     column_headers.append(column_headers.text) # doesn't return headers in our case, check with other examples too!!!
            # get table title
            try:
                table_title = table.title.text
            except AttributeError:
                table_title = None
            table_html = table.to_html()
            table_markdown = table.to_markdown()
            table_width = table.width
            table_x = table.x
            table_y = table.y
 
            # specify area to crop
            area_to_crop = (
                table_bbox.x * page_width,
                table_bbox.y * page_height,
                (table_bbox.x + table_bbox.width) * page_width,
                (table_bbox.y + table_bbox.height) * page_height
            )
 
            # crop page image based on table area
            page_img_cropped = page_image.crop(area_to_crop)
 
            # create a folder for the documnt to store the table if it doesn't exist:
            if not os.path.exists(f"{doc_name}/tables/img"):
                os.makedirs(f"{doc_name}/tables/img")
 
            table_img_path = f'{doc_name}/tables/img/{table_name}.png'
            # save the table in a png file
            page_img_cropped.save(table_img_path)
 
            # send the image of the "table" for LAYOUT analysis with Textract
            table_verification_analysis_doc_object = extractor.start_document_analysis(page_img_cropped,
                                                  s3_upload_path=s3_upload_path,
                                              features=[TextractFeatures.LAYOUT])
 
            # get layouts from the new analysis
            table_verification_layouts = table_verification_analysis_doc_object.layouts
            table_verification_layouts_types = []
            table_verification_layouts_conf = []
            for layout in table_verification_layouts:
                print('run loop 5')
 
                # print(layout)
                table_verification_layouts_types.append(layout.layout_type)
                table_verification_layouts_conf.append(layout.confidence)
 
            table_verification_layouts = [{'type': t, 'confidence': c} for t, c in zip(table_verification_layouts_types, table_verification_layouts_conf)]
 
            table_data = {
                "document_name": doc_name,
                "table_id": table_id,
                "table_name": table_name,
                "table_bbox": table_bbox,
                "table_column_count": table_column_count,
                "table_title": table_title,
                "column_headers": column_headers,
                "footers": footers,
                'table_height': table_height,
                'table_metadata': table_metadata,
                'table_page_number': table_page_number,
                'table_page_id': table_page_id,
                'table_confidence': table_confidence,
                'table_row_count': table_row_count,
                'table_img_path': table_img_path,
                'table_title': table_title,
                "table_html": table_html,
                "table_markdown": table_markdown,
                'table_width': table_width,
                'table_x': table_x,
                'table_t': table_y,
                'table_verification_layouts': table_verification_layouts
            }
 
            extracted_initial_table_list.append(table_data)
 
first_filter_pass_tables = []
 
for table in extracted_initial_table_list:
    table_verification_layouts_types = table['table_verification_layouts']
    # if analysed page returns a list with only 1 layout we will assume it's a table
    if len(table_verification_layouts_types) == 1:
        first_filter_pass_tables.append(table)
    # if analysed page returns a list with more than 1 layouts
    # we will check if a layout table is present and if the confidence is more than 90 in order to assume it's a table
    elif 'LAYOUT_TABLE' in table_verification_layouts_types and table.raw_object['Confidence'] > 90:
        first_filter_pass_tables.append(table)
 
final_filter_pass_tables = []
first_filter_pass_tables = []
 
for table in extracted_initial_table_list:
    table_verification_layouts_types = table['table_verification_layouts']
    # if analysed page returns a list with only 1 layout we will assume it's a table
    if len(table_verification_layouts_types) == 1:
        first_filter_pass_tables.append(table)
    # if analysed page returns a list with more than 1 layouts
    # we will check if a layout table is present and if the confidence is more than 90 in order to assume it's a table
    elif 'LAYOUT_TABLE' in table_verification_layouts_types and table.raw_object['Confidence'] > 90:
        first_filter_pass_tables.append(table)
 
for table in first_filter_pass_tables:
    # if a table hasn't more than 95% confidence we won't include it in final selection
    if table['table_confidence'] > 95:
        final_filter_pass_tables.append(table)
