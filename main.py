      metadata_dict = self.additional_metadata
               
 
        # Summary table preparation
        summary_table = [
            Document(
                page_content=f"{self.filename} {item.get('figure_page', '')} {item.get('table_title', '')} {' '.join(item.get('footers', []))} {' '.join(item.get('column_headers', []))} {' ' + item.get('table_html', '') if self.embed_raw_html else ''}".strip(),
               
                metadata={
                    **metadata_dict,
                    "page_number": item.get("figure_page", ""),
                    "document_name": self.filename,
                    "id_key": table_ids[index],
                    "type": "table",
                },
                self.page_num_collection_tables.append(page_content),
            )
            for index, item in enumerate(ghg_table)
        ]
       
 
        # HTML content extraction for tables
        html_content_list = [table["table_html"] for table in ghg_table]
        #asyncio.run(self.memory_store.mset(list(zip(table_ids, html_content_list))))
        await self.memory_store.mset(list(zip(table_ids, html_content_list)))
 
        return summary_table, table_id
