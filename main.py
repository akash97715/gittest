import openpyxl

def save_to_excel(data, filename):
    # Create a new workbook and select the active worksheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Write data to the worksheet
    for row_index, row in enumerate(data, start=1):
        for col_index, cell_value in enumerate(row, start=1):
            sheet.cell(row=row_index, column=col_index, value=cell_value)

    # Save the workbook to a file
    workbook.save(filename)

# Example usage
data = [
    ["Header1", "Header2", "Header3"],
    ["Row1-Cell1", "Row1-Cell2", "Row1-Cell3"],
    ["Row2-Cell1", "Row2-Cell2", "Row2-Cell3"],
    # Add more rows as needed
]

filename = 'output.xlsx'
save_to_excel(data, filename)
