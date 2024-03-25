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
        added_texts = set()  # Initialize a set to track the added texts and avoid duplication
        p = document.add_paragraph()

        for elem in soup.descendants:
            if isinstance(elem, NavigableString):
                text = str(elem).strip()
                if text and text not in added_texts:  # Add text if it's not empty and not added before
                    run = p.add_run(text)
                    self.apply_formatting(run, elem.parent.name)
                    added_texts.add(text)  # Add this text to the set of added texts
            elif elem.name in ['p', 'h1', 'h2', 'h3'] and elem.get_text() not in added_texts:
                # Add a new paragraph if the tag is p or a heading, but only if the text hasn't been added
                p = document.add_paragraph()
                run = p.add_run(elem.get_text())
                self.apply_formatting(run, elem.name)
                if elem.name in ['h1', 'h2', 'h3']:
                    run.bold = True
                    p.style = document.styles['Heading ' + elem.name[1]]
                run.font.size = Pt(12)
                added_texts.add(elem.get_text())  # Add the text of this element to the set

    def create_document(self):
        document = Document()
        for placeholder in self.payload['placeholders']:
            html_content = placeholder['content']['text']
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder['content'].get('citations')
            if citations:
                # Add the citations with a smaller font size, as plain text
                p = document.add_paragraph("Citations:\n")
                for citation in citations:
                    citation_text = f"Source: {citation['source']}, Page: {citation['page']}"
                    if citation_text not in added_texts:  # Check if the citation text has not been added yet
                        p.add_run(citation_text).font.size = Pt(8)
                        p.add_run("\n")  # Add a newline after each citation

        # Instead of saving the file directly, return a BytesIO object
        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob

# The payload variable should be defined as per your JSON structure here

# Example usage
doc_creator = DocumentCreator(payload)
docx_blob = doc_creator.create_document()

# Save the DOCX to a file
file_path = "document.docx"  # Update with your desired path
with open(file_path, "wb") as f:
    f.write(docx_blob.getvalue())

print(f"Document saved to {file_path}.")
