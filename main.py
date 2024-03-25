from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt
from io import BytesIO

class DocumentCreator:
    def __init__(self, payload):
        self.payload = payload

    @staticmethod
    def add_run(paragraph, text, bold=False, italic=False, underline=False, font_size=12):
        run = paragraph.add_run(text)
        run.bold = bold
        run.italic = italic
        run.underline = underline
        run.font.size = Pt(font_size)
        return run

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        for elem in soup.children:
            if elem.name == 'p':
                p = document.add_paragraph()
                for format_elem in elem:
                    if isinstance(format_elem, str):
                        self.add_run(p, format_elem)
                    else:
                        # Apply the formatting as per the tag
                        bold = format_elem.name in ['strong', 'b']
                        italic = format_elem.name in ['em', 'i']
                        underline = format_elem.name == 'u'
                        self.add_run(p, format_elem.text, bold, italic, underline)
            elif elem.name in ['h1', 'h2', 'h3']:
                p = document.add_paragraph()
                self.add_run(p, elem.text, bold=True)
                p.style = document.styles['Heading ' + elem.name[1]]

    def create_document(self):
        document = Document()
        for placeholder in self.payload['placeholders']:
            html_content = placeholder['content']['text']
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder['content'].get('citations')
            if citations:
                p = document.add_paragraph("Citations:\n")
                # Assuming citations are a list of dictionaries, we format them as a string here.
                citations_text = '\n'.join([f"Source: {c['source']}, Page: {c['page']}" for c in citations])
                self.add_run(p, citations_text, font_size=8)

        # Instead of saving the file directly, return a BytesIO object
        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob

# Create an instance of the document creator with the provided payload
doc_creator = DocumentCreator(payload)
# Generate the document
docx_blob = doc_creator.create_document()

# Save the document to a file for download (example for a web server)
file_path = "/path/to/document.docx"  # Replace with your desired path
with open(file_path, "wb") as f:
    f.write(docx_blob.getvalue())

print(f"Document saved to {file_path}.")
