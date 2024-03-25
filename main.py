rom bs4 import BeautifulSoup, NavigableString
from docx import Document
from docx.shared import Pt
from io import BytesIO


class DocumentCreator:
    def __init__(self, payload):
        self.payload = payload

    @staticmethod
    def apply_formatting(run, tag):
        # Apply formatting based on the tag
        if tag in ["strong", "b"]:
            run.bold = True
        if tag in ["em", "i"]:
            run.italic = True
        if tag == "u":
            run.underline = True

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        added_texts = set()  # Set to keep track of added texts to avoid repetition

        for elem in soup.descendants:
            if isinstance(elem, NavigableString):
                text = str(elem).strip()
                parent_tag = elem.parent.name if elem.parent else None
                if (
                    text
                    and parent_tag not in ["p", "h1", "h2", "h3"]
                    and text not in added_texts
                ):
                    run = document.add_paragraph().add_run(text)
                    self.apply_formatting(run, parent_tag)
                    added_texts.add(text)
            elif elem.name in ["p", "h1", "h2", "h3"]:
                text = elem.get_text(strip=True)
                if text not in added_texts:
                    p = document.add_paragraph()
                    run = p.add_run(text)
                    self.apply_formatting(run, elem.name)
                    if elem.name in ["h1", "h2", "h3"]:
                        run.bold = True
                        p.style = document.styles["Heading " + elem.name[1]]
                    run.font.size = Pt(12)
                    added_texts.add(text)

    def create_document(self):
        document = Document()
        for placeholder in self.payload["placeholders"]:
            html_content = placeholder["content"]["text"]
            # print("added text",html_content)
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder["content"].get("citations")
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
