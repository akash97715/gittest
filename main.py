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
        if tag in ['strong', 'b']:
            run.bold = True
        if tag in ['em', 'i']:
            run.italic = True
        if tag == 'u':
            run.underline = True

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        p = document.add_paragraph()
        added_texts = set()  # Set to keep track of added texts

        for elem in soup.descendants:
            if isinstance(elem, NavigableString):
                text = str(elem).strip()
                if text and text not in added_texts:  # Check if the text has not been added yet
                    run = p.add_run(text)
                    self.apply_formatting(run, elem.parent.name)
                    added_texts.add(text)  # Mark the text as added
            elif elem.name in ['p', 'h1', 'h2', 'h3']:
                # Add a new paragraph if the tag is p or a heading
                if elem.get_text(strip=True) not in added_texts:  # Check for repetition
                    p = document.add_paragraph()
                    run = p.add_run(elem.get_text(strip=True))
                    self.apply_formatting(run, elem.name)
                    if elem.name in ['h1', 'h2', 'h3']:
                        run.bold = True
                        p.style = document.styles['Heading ' + elem.name[1]]
                    run.font.size = Pt(12)
                    added_texts.add(elem.get_text(strip=True))  # Mark the text as added

    def create_document(self):
        document = Document()
        for placeholder in self.payload['placeholders']:
            html_content = placeholder['content']['text']
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder['content'].get('citations')
            if citations:
                # Add the citations with a smaller font size, as plain text
                citation_text = "Citations:\n" + "\n".join(
                    [f"Source: {c['source']}, Page: {c['page']}" for c in citations]
                )
                p = document.add_paragraph(citation_text)
                for run in p.runs:
                    run.font.size = Pt(8)

        # Instead of saving the file directly, return a BytesIO object
        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob
