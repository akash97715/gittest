extractor = Textractor(profile_name="default")
tables_analysis_doc_object = extractor.start_document_analysis(f"Docs/{doc_name}",
                                                  s3_upload_path=s3_upload_path,
                                              features=[TextractFeatures.TABLES])
