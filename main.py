from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt
from io import BytesIO

class DocumentCreator:
    def __init__(self, payload):
        self.payload = payload

    @staticmethod
    def apply_formatting(run, elem):
        if elem.name == 'strong':
            run.bold = True
        elif elem.name == 'em':
            run.italic = True
        elif elem.name == 'u':
            run.underline = True
        # Set default font size
        run.font.size = Pt(12)

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, features="html.parser")
        for elem in soup.find_all(['h1', 'h2', 'h3', 'p']):
            # For each tag, add a new paragraph and run with proper formatting.
            p = document.add_paragraph()
            for content in elem.contents:
                if isinstance(content, NavigableString):
                    run = p.add_run(content)
                else:
                    run = p.add_run(content.text)
                    self.apply_formatting(run, content)
            # After finishing a tag, we add a line break if it's a heading.
            if elem.name in ['h1', 'h2', 'h3']:
                p.add_run().add_break()

    def add_citations_to_docx(self, document, citations):
        p = document.add_paragraph("Citations:\n")
        for citation in citations:
            p.add_run(f"Source: {citation['source']}, Page: {citation['page']}\n").font.size = Pt(8)

    def create_document(self):
        document = Document()
        for placeholder in self.payload.get("placeholders", []):
            html_content = placeholder.get("content", {}).get("text", "")
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder.get("content", {}).get("citations", [])
            if citations:
                self.add_citations_to_docx(document, citations)

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
with open(output
