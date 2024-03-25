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
        added_content = set()  # Track added content to avoid duplicates
        p = document.add_paragraph()

        for elem in soup.descendants:
            if isinstance(elem, NavigableString):
                parent_tag = elem.parent.name if elem.parent else None
                if str(elem).strip() and str(elem) not in added_content:
                    run = p.add_run(str(elem))
                    self.apply_formatting(run, parent_tag)
                    added_content.add(str(elem))
            elif elem.name in ['p', 'h1', 'h2', 'h3'] and elem not in added_content:
                # Only add a new paragraph if we're not already processing one, to avoid duplicate breaks
                if p.text or p.runs:  # Check if paragraph already has content before adding a new one
                    p = document.add_paragraph()
                run = p.add_run(elem.text.strip())
                self.apply_formatting(run, elem.name)
                added_content.add(elem)

    def create_document(self):
        document = Document()
        for placeholder in self.payload.get("placeholders", []):
            html_content = placeholder.get("content", {}).get("text", "")
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder.get("content", {}).get("citations", "")
            if citations:
                citation_text = "Citations:\n" + "\n".join(
                    [f"Source: {c['source']}, Page: {c['page']}" for c in citations]
                )
                p = document.add_paragraph()
                citation_run = p.add_run(citation_text)
                citation_run.font.size = Pt(8)  # Set font size for citations to 8

        # Instead of saving the file directly, return a BytesIO object
        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob

doc_creator = DocumentCreator(payload)
docx_blob = doc_creator.create_document()

# Example for saving the DOCX
file_path = "your_document_path_here.docx"  # Adjust this path
with open(file_path, "wb") as f:
    f.write(docx_blob.getvalue())

print("Document saved.")
