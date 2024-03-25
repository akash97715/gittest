from bs4 import BeautifulSoup, NavigableString
from docx import Document
from docx.shared import Pt
from io import BytesIO

class DocumentCreator:
    def __init__(self, payload):
        self.payload = payload

    def process_element(self, element, document):
        """Process individual HTML elements and add them to the DOCX document with formatting."""
        if isinstance(element, NavigableString):
            # Directly add navigable strings that are not just whitespace
            if element.strip():
                p = document.add_paragraph(element.strip())
                p.runs[0].font.size = Pt(12)  # Default font size for all text
        elif element.name in ['p', 'h1', 'h2', 'h3']:
            # Create a new paragraph for p and heading elements, apply styles for headings
            text = element.get_text(strip=True)
            if text:  # Ensure there's text to add
                if element.name in ['h1', 'h2', 'h3']:
                    p = document.add_paragraph(text, style='Heading ' + element.name[1])
                else:
                    p = document.add_paragraph(text)
                p.runs[0].font.size = Pt(12)
        # For formatting tags within paragraphs (e.g., <strong>, <em>, <u>), this simple approach does not apply formatting.
        # You might need to extend the logic here for a more comprehensive solution.

    def add_html_content_to_docx(self, document, html_content):
        """Convert HTML content to DOCX format."""
        soup = BeautifulSoup(html_content, "html.parser")
        for elem in soup.find_all(['p', 'h1', 'h2', 'h3', NavigableString], recursive=False):
            self.process_element(elem, document)

    def create_document(self):
        """Create the DOCX document based on the placeholders in the payload."""
        document = Document()
        for placeholder in self.payload.get("placeholders", []):
            html_content = placeholder.get("content", {}).get("text", "")
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder.get("content", {}).get("citations", "")
            if citations:
                # Add citations with a smaller font size
                citation_text = "\n".join(f"Source: {c['source']}, Page: {c['page']}" for c in citations)
                p = document.add_paragraph("Citations:\n" + citation_text)
                p.runs[0].font.size = Pt(8)

        # Return a BytesIO object containing the DOCX file
        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob

# Example usage
doc_creator = DocumentCreator(payload)
docx_blob = doc_creator.create_document()

# Example for saving the DOCX, replace "your_document_path_here.docx" with your actual file path
file_path = "/path/to/your_document.docx"
with open(file_path, "wb") as f:
    f.write(docx_blob.getvalue())

print("Document saved.")
