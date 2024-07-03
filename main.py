def _gather_table_metadata(self, table, table_img_path, page_num):
        column_headers = [
            cell.text for cell in table.table_cells if cell.is_column_header
        ]
        footers = [footer.text for footer in table.footers]
 
        return {
            "document_path": self.custom_extraction_document_path,
            "table_id": table.id,
            "figure_name": os.path.basename(table_img_path),
            "table_bbox": table.bbox,
            "table_column_count": table.column_count,
            "table_title": getattr(table.title, "text", None),
            "column_headers": column_headers,
            "footers": footers,
            "table_height": table.height,
            "table_metadata": table.metadata,
            "figure_page": page_num,
            "table_page_id": table.page_id,
            "table_confidence": table.raw_object["Confidence"],
            "table_row_count": table.row_count,
            "table_img_path": table_img_path,
            "table_html": table.to_html(),
            "table_markdown": table.to_markdown(),
            "table_width": table.width,
            "table_x": table.x,
            "table_y": table.y,
            "table_embedding_text": table.get_text(
                TextLinearizationConfig(
                    table_linearization_format="markdown",
                    table_flatten_headers=True,
                    table_duplicate_text_in_merged_cells=True,
                    table_column_header_threshold=0.5,
                )
            ),
        }
