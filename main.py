 def _update_ingestion_status_table(self, source_table_name: str, destination_table_name: str) -> None:
        try:
            with self.source_conn.conn.cursor() as source_cursor, self.destination_conn.conn.cursor() as destination_cursor:
                # Retrieve data from the source table for client IDs in the mapping dictionary
                client_ids_to_fetch = self.id_mapping
                client_ids_placeholder = ','.join(['%s'] * len(client_ids_to_fetch))
                source_cursor.execute(f"SELECT * FROM {source_table_name} WHERE client_id IN ({client_ids_placeholder}) AND Status = 'Completed' AND is_file_deleted = false", client_ids_to_fetch)
                data_to_copy = source_cursor.fetchall()
 
                # Insert data into the destination table
                for row in data_to_copy:
                    # Replace client IDs in the row with mapped values
                    mapped_row = self.replace_client_ids(row)
 
                    # Define the INSERT query with placeholders
                    insert_query = f"INSERT INTO {destination_table_name} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"  # Replace with the correct number of placeholders
 
                    # Execute the INSERT query with the mapped row data
                    destination_cursor.execute(insert_query, mapped_row)
 
            # Commit the changes to the destination database
            self.destination_conn.conn.commit()
