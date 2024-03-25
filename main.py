from bs4 import BeautifulSoup, NavigableString
from docx import Document
from docx.shared import Pt
from io import BytesIO

class DocumentCreator:
    def __init__(self, payload):
        self.payload = payload

    def apply_formatting(self, run, tag):
        # Apply formatting based on the tag
        if tag in ['strong', 'b']:
            run.bold = True
        if tag in ['em', 'i']:
            run.italic = True
        if tag == 'u':
            run.underline = True
        run.font.size = Pt(12)

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        elements_to_add = []

        for elem in soup.body:
            if isinstance(elem, NavigableString):
                if elem.strip():
                    elements_to_add.append({'text': elem.strip(), 'tag': None})
            elif isinstance(elem, Tag):
                if elem.name in ['p', 'h1', 'h2', 'h3']:
                    text = ''.join(elem.stripped_strings)
                    elements_to_add.append({'text': text, 'tag': elem.name})

        for elem in elements_to_add:
            if elem['tag'] in ['h1', 'h2', 'h3']:
                p = document.add_paragraph(elem['text'], style='Heading ' + elem['tag'][1])
            else:
                p = document.add_paragraph(elem['text'])
            if elem['tag']:
                run = p.runs[0]
                self.apply_formatting(run, elem['tag'])
            else:
                p.runs[0].font.size = Pt(12)

    def create_document(self):
        document = Document()
        for placeholder in self.payload.get("placeholders", []):
            html_content = placeholder.get("content", {}).get("text", "")
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder.get("content", {}).get("citations", "")
            if citations:
                p = document.add_paragraph("Citations:\n")
                for c in citations:
                    citation_text = f"Source: {c['source']}, Page: {c['page']}"
                    citation_run = p.add_run(citation_text)
                    citation_run.font.size = Pt(8)
                    p.add_run("\n")  # Add a new line after each citation

        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob

# Example usage
doc_creator = DocumentCreator(payload)
docx_blob = doc_creator.create_document()

# Save the DOCX to a file
file_path = "/path/to/your_document.docx"  # Update with the path where you want
