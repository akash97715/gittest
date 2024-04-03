def _update_ingestion_status_table(self, source_table_name: str, destination_table_name: str, batch_size=1000) -> None:
    try:
        with self.source_conn.conn.cursor() as source_cursor, self.destination_conn.conn.cursor() as destination_cursor:
            # Retrieve data from the source table for client IDs in the mapping dictionary
            client_ids_to_fetch = tuple(self.id_mapping.keys())
            client_ids_placeholder = ','.join(['%s'] * len(client_ids_to_fetch))
            source_cursor.execute(f"SELECT * FROM {source_table_name} WHERE client_id IN ({client_ids_placeholder}) AND Status = 'Completed' AND is_file_deleted = false", client_ids_to_fetch)
            data_to_copy = source_cursor.fetchall()
 
            # Prepare for batch insertion
            mapped_rows = [self.replace_client_ids(row) for row in data_to_copy]
            insert_query = f"INSERT INTO {destination_table_name} VALUES ({', '.join(['%s'] * 15)})"  # Assuming 15 columns as per your placeholders
 
            # Execute batch inserts
            for i in range(0, len(mapped_rows), batch_size):
                batch = mapped_rows[i:i+batch_size]
                destination_cursor.executemany(insert_query, batch)
 
        # Commit the changes to the destination database
        self.destination_conn.conn.commit()
    except Exception as e:
        # Handle exception, possibly roll back transaction
        print(f"An error occurred: {e}")
        self.destination_conn.conn.rollback()
