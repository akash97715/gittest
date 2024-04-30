        summary_table = [
            Document(
                page_content=f"{self.filename} {item.get('figure_page', '')} {item.get('table_title', '')} {' '.join(item.get('footers', []))} {' '.join(item.get('column_headers', []))}".strip(),
                metadata={
                    **metadata_dict,
                    "page_number": item.get("figure_page", ""),
                    "document_name": self.filename,
                    "id_key": table_ids[index],
                    "type":"table",
                },
            )
            for index, item in enumerate(ghg_table)
        ]
