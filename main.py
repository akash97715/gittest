summary_table = []
for index, item in enumerate(ghg_table):
    page_content = f"{self.filename} {item.get('figure_page', '')} {item.get('table_title', '')} {' '.join(item.get('footers', []))} {' '.join(item.get('column_headers', []))} {' ' + item.get('table_html', '') if self.embed_raw_html else ''}".strip()
    summary_table.append(Document(
        page_content=page_content,
        metadata={
            **metadata_dict,
            "page_number": item.get("figure_page", ""),
            "document_name": self.filename,
            "id_key": table_ids[index],
            "type": "table",
        }
    ))
    self.page_num_collection_tables.append(page_content)
