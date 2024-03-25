from bs4 import BeautifulSoup, NavigableString, Tag
from docx import Document
from docx.shared import Pt
from io import BytesIO

class DocumentCreator:
    def __init__(self, payload):
        self.payload = payload

    @staticmethod
    def apply_formatting(run, tag):
        # Apply formatting based on the tag
        if tag.name in ['strong', 'b']:
            run.bold = True
        if tag.name in ['em', 'i']:
            run.italic = True
        if tag.name == 'u':
            run.underline = True

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        for elem in soup.body.contents:  # Only directly iterate over the body's direct children
            if isinstance(elem, NavigableString):
                p = document.add_paragraph(str(elem).strip())
            elif isinstance(elem, Tag):
                if elem.name in ['h1', 'h2', 'h3']:
                    p = document.add_paragraph(style='Heading ' + elem.name[1])
                else:
                    p = document.add_paragraph()
                for content in elem.contents:
                    if isinstance(content, NavigableString):
                        run = p.add_run(str(content).strip())
                        self.apply_formatting(run, elem)
                p.runs[0].font.size = Pt(12)  # Set font size for the paragraph

    def create_document(self):
        document = Document()
        for placeholder in self.payload.get("placeholders", []):
            html_content = placeholder.get("content", {}).get("text", "")
            if html_content:  # Check for None or empty string
                self.add_html_content_to_docx(document, html_content)

            citations = placeholder.get("content", {}).get("citations", [])
            if citations:  # Check for None or empty list
                p = document.add_paragraph("Citations:\n")
                for citation in citations:
                    citation_text = f"Source: {citation['source']}, Page: {citation['page']}\n"
                    p.add_run(citation_text).font.size = Pt(8)

        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob

# Example payload provided in the user's input format
payload = {
    # ... (insert the entire payload structure here)
}

# Create the document
doc_creator = DocumentCreator(payload)
docx_blob = doc_creator.create_document()

# Write the DOCX file to disk
output_path = '/path/to/output/document.docx'  # Update with your desired output path
with open(output_path, 'wb') as f:
    f.write(docx_blob.getvalue())

print(f'Document created and saved to {output_path}')
