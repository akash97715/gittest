from bs4 import BeautifulSoup, NavigableString, Tag
from docx import Document
from docx.shared import Pt
from io import BytesIO

class DocumentCreator:
    def __init__(self, payload):
        self.payload = payload

    @staticmethod
    def apply_formatting(run, tag):
        # Check for and apply text formatting based on the HTML tag.
        if tag in ['b', 'strong']:
            run.bold = True
        elif tag in ['i', 'em']:
            run.italic = True
        elif tag == 'u':
            run.underline = True
        # Font size is set later, individually for main content and citations.

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # Start with a default paragraph.
        p = document.add_paragraph()

        for elem in soup.descendants:
            if isinstance(elem, NavigableString):
                if elem.parent.name == 'p':
                    # Add a new paragraph for each <p> tag.
                    p = document.add_paragraph()
                run = p.add_run(str(elem))
                self.apply_formatting(run, elem.parent.name)
                # Apply a standard font size for all text.
                run.font.size = Pt(12)

            elif isinstance(elem, Tag) and elem.name in ['h1', 'h2', 'h3']:
                # Add a heading and apply the heading style.
                p = document.add_paragraph()
                run = p.add_run(elem.get_text())
                run.bold = True
                p.style = document.styles['Heading ' + elem.name[1]]
                p.add_run().add_break()  # Add a break after heading for spacing.

    def create_document(self):
        document = Document()
        for placeholder in self.payload.get("placeholders", []):
            html_content = placeholder.get("content", {}).get("text", "")
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder.get("content", {}).get("citations", "")
            if citations:
                # Add the citations with a smaller font size, as plain text.
                p = document.add_paragraph("Citations:\n")
                citation_run = p.add_run(citations)
                citation_run.font.size = Pt(8)

        # Instead of saving the file directly, we return a BytesIO object.
        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob
