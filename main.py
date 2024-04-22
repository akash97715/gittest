# Sample metadata and payload
metadata_dict = {'doc_name': 'something', 'doc_md5': '14516542652'}
payload = [
    {'document_name': 'tobeingest', 'page_num': 1, 'page_full_text': 'Inflammatory Bowel Diseases, XXXX, XX, 1-12\n...'}
    # Add other documents as needed
]

# Document class
class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

# Function to create a list of Document objects using list comprehension
def create_documents_from_payload(payload, base_metadata):
    return [
        Document(
            item['page_full_text'],
            {**base_metadata, 'document_name': item['document_name'], 'page_number': item['page_num']}
        ) for item in payload
    ]

# Create documents
documents = create_documents_from_payload(payload, metadata_dict)

# Output the documents (for demonstration)
for doc in documents:
    print(doc.page_content[:100])  # Print first 100 characters of page content for brevity
    print(doc.metadata)            # Print metadata
