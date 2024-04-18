layout_analysis_doc_object = extractor.start_document_analysis(file_source="s3://sbx-docinsight-ocr/[II_MANU_01_OUT_01]Odufalu FD MS OUTPUT.pdf",
                                                  s3_upload_path=s3_upload_path,
                                              features=[TextractFeatures.LAYOUT])
layout_analysis_doc_object.layouts
