# Replace these placeholder values with your actual parameters
file_source = "s3://your-bucket/your-document.pdf"
doc_name = "YourDocName"
s3_upload_path = "s3://your-upload-path/"

# Assuming `extractor` is an instance of a class with async methods that handle document analysis
# Initialize the DocumentAnalyzer with your configured parameters
document_analyzer = DocumentAnalyzer(extractor, file_source, doc_name, s3_upload_path)

# To extract figures
await document_analyzer.extract_figures()

# To extract tables
await document_analyzer.extract_tables()

# Output the results to see what has been extracted
print(document_analyzer.extracted_figures)
print(document_analyzer.extracted_tables)
