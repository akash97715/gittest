[12:32 PM] Deep, Akash (External)
        metering_data={'totalPages':total_pages,'totalTable':self.total_extracted_tables, 'filteredTable':len(self.extracted_tables),  'advTableFilter':self.advance_table_filter}
       
        total_pages_temp = metering_data.get('metering_data', {}).get('totalPages', 0)
        adv_table_filter = metering_data.get('metering_data', {}).get('advTableFilter', False)
        total_table = metering_data.get('metering_data', {}).get('totalTable', 0)
        total_pages = total_pages_temp if not adv_table_filter else total_pages_temp + total_table
