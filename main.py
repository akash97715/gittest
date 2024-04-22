import uuid

# Document class definition
class Document:
    def __init__(self, page_contents, metadata):
        self.page_contents = page_contents
        self.metadata = metadata

# Sample metadata dictionary
metadata_dict = {'doc_name': 'something', 'doc_md5': '14516542652'}

# Sample payload
text_summaries = [
    {'document_name': 'tobeingest', 'page_num': 1, 'page_full_text': 'Inflammatory Bowel Diseases, XXXX, XX, 1-12\n...'}
    # Add other documents as needed
]

# Creating UUIDs for each document
doc_ids = [str(uuid.uuid4()) for _ in text_summaries]

# Creating a list of Document objects using list comprehension
summary_texts = [
    Document(
        page_contents=item['page_full_text'],
        metadata={
            **metadata_dict,
            'document_name': item['document_name'],
            'page_number': item['page_num'],
            'doc_uuid': doc_ids[index]  # Assigning UUID from the generated list
        }
    )
    for index, item in enumerate(text_summaries)
]

# Output the documents (for demonstration)
for doc in summary_texts:
    print(doc.page_contents[:100])  # Print first 100 characters of page content for brevity
    print(doc.metadata)             # Print metadata
