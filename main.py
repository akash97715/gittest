class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(page_content={self.page_content}, metadata={self.metadata})"

class MyClass:
    def __init__(self):
        self.table_documents = []  # This would be filled with Document instances for tables
        self.image_documents = []  # This would be filled with Document instances for images

    def combine_documents(self):
        # Initialize empty lists for combined contents
        combined_page_content_list = []
        combined_metadata_content_list = []

        # Combine table documents
        combined_page_content_list += [doc.page_content for doc in self.table_documents]
        combined_metadata_content_list += [doc.metadata for doc in self.table_documents]

        # Combine image documents
        combined_page_content_list += [doc.page_content for doc in self.image_documents]
        combined_metadata_content_list += [doc.metadata for doc in self.image_documents]

        return combined_page_content_list, combined_metadata_content_list

# Example usage
my_class_instance = MyClass()
# Suppose `my_class_instance.table_documents` and `my_class_instance.image_documents` are populated with Document instances
# For example:
my_class_instance.table_documents.append(Document("Table Content 1", {"id": "001", "type": "table"}))
my_class_instance.table_documents.append(Document("Table Content 2", {"id": "002", "type": "table"}))
my_class_instance.image_documents.append(Document("Image Content 1", {"id": "003", "type": "image"}))
my_class_instance.image_documents.append(Document("Image Content 2", {"id": "004", "type": "image"}))

# Get combined content and metadata
page_contents, metadatas = my_class_instance.combine_documents()
print("Combined Page Contents:", page_contents)
print("Combined Metadatas:", metadatas)
