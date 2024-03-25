from bs4 import BeautifulSoup, NavigableString
from docx import Document
from docx.shared import Pt
from io import BytesIO

class DocumentCreator:
    def __init__(self, payload):
        self.payload = payload

    @staticmethod
    def apply_formatting(run, tag):
        # Apply formatting based on the tag
        if tag.name in ['b', 'strong']:
            run.bold = True
        if tag.name in ['i', 'em']:
            run.italic = True
        if tag.name == 'u':
            run.underline = True
        # Set the font size for all text
        run.font.size = Pt(12)

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        for elem in soup.contents:
            if isinstance(elem, NavigableString):
                if elem.parent.name not in ['h1', 'h2', 'h3']:
                    p = document.add_paragraph()
                    run = p.add_run(str(elem))
                    self.apply_formatting(run, elem.parent)
            elif elem.name in ['h1', 'h2', 'h3']:
                p = document.add_paragraph()
                run = p.add_run(elem.get_text())
                run.bold = True
                p.style = document.styles['Heading ' + elem.name[1]]
            elif elem.name in ['p', 'b', 'strong', 'i', 'em', 'u']:
                p = document.add_paragraph()
                for sub_elem in elem.contents:
                    if isinstance(sub_elem, NavigableString):
                        run = p.add_run(str(sub_elem))
                        self.apply_formatting(run, elem)

    def create_document(self):
        document = Document()
        for placeholder in self.payload.get("placeholders", []):
            html_content = placeholder.get("content", {}).get("text", "")
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder.get("content", {}).get("citations", "")
            if citations:
                # Add citations as plain text with a smaller font size
                p = document.add_paragraph("Citations:\n")
                citation_run = p.add_run(citations)
                citation_run.font.size = Pt(8)  # Set font size for citations to 8

        # Instead of saving the file directly, return a BytesIO object
        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob
