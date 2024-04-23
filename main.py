def table_to_html(table):
    html = "<table border='1'>\n"  # Added border for visibility
    for row in range(table.rows):  # Assuming table.rows gives the count of rows
        html += "<tr>\n"
        for column in range(table.columns):  # Assuming table.columns gives the count of columns
            # You would need to access the text of each cell
            # Assuming 'table.get_cell(row, column)' method to get the cell at a specific position
            # Replace 'get_cell(row, column)' with the actual method to access cells in your table object
            cell_text = table.get_cell(row, column).text if table.get_cell(row, column) else ""
            html += f"<td>{cell_text}</td>\n"
        html += "</tr>\n"
    html += "</table>"
    return html

# You would replace 'table.to_html()' in your original code with 'table_to_html(table)'
