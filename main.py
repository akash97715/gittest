# Assuming you have an 'extractor' object that's configured to handle AWS Textract operations or a similar service

# Define parameters
file_source = "s3://sbx-docinsight-ocr/[II_MANU_01_OUT_01]Odufalu FD MS OUTPUT.pdf"
doc_name = "DocumentName"  # This will be used for saving files locally
s3_upload_path = "s3://desired-upload-path/"

# Create an instance of DocumentAnalyzer
document_analyzer = DocumentAnalyzer(extractor=extractor, file_source=file_source, doc_name=doc_name, s3_upload_path=s3_upload_path)

# To extract figures from the document
document_analyzer.extract_figures()

# To extract tables from the document
document_analyzer.extract_tables()

# The results will be stored in `document_analyzer.extracted_figures` and `document_analyzer.extracted_tables`
# You can access these lists to see the data or further process them
print("Extracted Figures:", document_analyzer.extracted_figures)
print("Extracted Tables:", document_analyzer.extracted_tables)
