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
