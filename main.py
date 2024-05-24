# Initialize metering_data dictionary
metering_data = {
    'totalPages': total_pages,
    'totalTable': self.total_extracted_tables,
    'filteredTable': len(self.extracted_tables),
    'advTableFilter': self.advance_table_filter
}

# Retrieve values from metering_data
total_pages_temp = metering_data.get('totalPages', 0)
adv_table_filter = metering_data.get('advTableFilter', False)
total_table = metering_data.get('totalTable', 0)

# Determine the final value of total_pages based on adv_table_filter
total_pages = total_pages_temp if not adv_table_filter else total_pages_temp + total_table
