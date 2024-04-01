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
        run.font.size = Pt(12)  # Apply font size uniformly
        run.font.name='sans-serif'
 
    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        added_texts = set()  # Set to keep track of added texts
 
        for elem in soup.descendants:
            if isinstance(elem, NavigableString):
                text = str(elem).strip()
                if text and text not in added_texts:  # Avoid duplication
                    if elem.parent.name not in ['p', 'h1', 'h2', 'h3', 'body']:
                        # If the string is not wrapped in a paragraph or heading, add it directly
                        run = document.add_paragraph().add_run(text)
                        self.apply_formatting(run, elem.parent.name)
                        added_texts.add(text)
            elif elem.name in ['p', 'h1', 'h2', 'h3']:
                # Add the text of the tags but avoid duplication if it's the same as NavigableString
                full_text = ''.join(elem.stripped_strings)
                if full_text not in added_texts:
                    p = document.add_paragraph()
                    for content in elem.contents:
                        if isinstance(content, NavigableString):
                            text = str(content).strip()
                            if text:
                                run = p.add_run(text)
                                self.apply_formatting(run, content.parent.name)
                        else:
                            # For other tags like <strong>, <em>, <u>, apply formatting
                            run = p.add_run(content.get_text(strip=True))
                            self.apply_formatting(run, content.name)
                    if elem.name in ['h1', 'h2', 'h3']:
                        p.style = document.styles['Heading ' + elem.name[1]]
                    added_texts.add(full_text)
 
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
                    source = citation['filename'] if citation['filename'].strip() else "N/A"
                    page = str(citation['page']) if str(citation['page']).strip() else "N/A"
                    section = str(citation['section']) if str(citation['section']).strip() else "N/A"
                    citation_text = f"Filename: {source}, Page: {page}, Section: {section}\n"                
                    run=p.add_run(citation_text)
                    run.font.size = Pt(8)
                    run.font.name = 'sans-serif'
 
 
        # Instead of saving the file directly, return a BytesIO object
        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob
