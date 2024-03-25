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
        if tag in ['strong', 'b']:
            run.bold = True
        if tag in ['em', 'i']:
            run.italic = True
        if tag == 'u':
            run.underline = True

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        for elem in soup.recursiveChildGenerator():
            if isinstance(elem, NavigableString) and not isinstance(elem.parent, Tag):
                continue  # Skip NavigableStrings that are children of Tags, since Tag handles them.
            if isinstance(elem, Tag):  # If the element is a tag
                if elem.name == 'p':
                    # Start a new paragraph for each <p> tag.
                    p = document.add_paragraph()
                    for content in elem.contents:
                        if isinstance(content, NavigableString):
                            run = p.add_run(str(content))
                            self.apply_formatting(run, elem.name)
                elif elem.name in ['h1', 'h2', 'h3']:
                    # Start a new paragraph and apply the heading style.
                    p = document.add_paragraph(style=document.styles['Heading ' + elem.name[1]])
                    p.add_run(elem.text)
                elif elem.name in ['b', 'strong', 'i', 'em', 'u']:
                    # If the tag is bold, italic, or underline, apply the appropriate formatting.
                    parent = elem.find_parent(['p', 'h1', 'h2', 'h3'])
                    if parent.name == 'p':
                        # Make sure we're still in the same paragraph.
                        run = p.add_run(elem.text)
                        self.apply_formatting(run, elem.name)

    def create_document(self):
        document = Document()
        for placeholder in self.payload['placeholders']:
            html_content = placeholder['content']['text']
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder['content'].get('citations')
            if citations:
                # Add the citations with a smaller font size, as plain text.
                p = document.add_paragraph("Citations:\n")
                for c in citations:
                    citation_text = f"Source: {c['source']}, Page: {c['page']}"
                    run = p.add_run(citation_text)
                    run.font.size = Pt(8)  # Set font size for citations to 8
                    p.add_run("\n")  # Add a new line after each citation

        # Instead of saving the file directly, return a BytesIO object
        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob
