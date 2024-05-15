total_pages = additional_metadata_details.get('metering_data', {}).get('totalPages', 0)
adv_table_filter = additional_metadata_details.get('metering_data', {}).get('advTableFilter', False)
total_table = additional_metadata_details.get('metering_data', {}).get('totalTable', 0)

result = total_pages if not adv_table_filter else total_pages + total_table
