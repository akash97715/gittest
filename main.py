if TEXTRACT_ENABLED and file_type in ['.pdf','.PDF']:
                            total_pages=total_pages
                        elif rw.extract_table_image_element and file_type in ['.pdf','.PDF']:
                            total_pages_temp = additional_metadata_details.get('metering_data', {}).get('totalPages', 0)
                            adv_table_filter = additional_metadata_details.get('metering_data', {}).get('advTableFilter', False)
                            total_table = additional_metadata_details.get('metering_data', {}).get('totalTable', 0)
                            total_pages = total_pages_temp if not adv_table_filter else total_pages + total_table
                            print("PUSHING TASK=============================================")
 
                        push_metrics()
