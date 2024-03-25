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

        for elem in soup.descendants:
            if isinstance(elem, NavigableString):
                if elem.strip():  # Avoid adding empty strings
                    run = p.add_run(str(elem))
                    self.apply_formatting(run, elem.parent.name)
            elif elem.name in ['p', 'h1', 'h2', 'h3']:
                # Add a new paragraph if the tag is p or a heading
                p = document.add_paragraph()
                run = p.add_run(elem.get_text())
                self.apply_formatting(run, elem.name)
                if elem.name in ['h1', 'h2', 'h3']:
                    run.bold = True
                    p.style = document.styles['Heading ' + elem.name[1]]
                # For a paragraph, apply the default font size
                run.font.size = Pt(12)

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

# Use the payload provided in the true/false/null form as required by the code
doc_creator = DocumentCreator(payload)
docx_blob = doc_creator.create_document()

# Save the document to a file for download (example for a web server)
file_path = "/path/to/document.docx"  # Replace with your desired path
with open(file_path, "wb") as f:
    f.write(docx_blob.getvalue())

print(f"Document saved to {file_path}.")
