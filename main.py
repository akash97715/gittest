# Extracting values with defaults to ensure robustness
page_number = item.get('table_page_number', '')
table_title = item.get('table_title', '')
footers = ' '.join(item.get('footers', []))  # Concatenate footer items into a single string
headers = ' '.join(item.get('headers', []))  # Concatenate header items into a single string

# Formatting the page content with clear variable insertion
page_content = f"{self.filename} {page_number} {table_title} {headers} {footers}".strip()
