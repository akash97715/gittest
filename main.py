from bs4 import BeautifulSoup, NavigableString
from docx import Document
from docx.shared import Pt
from io import BytesIO

# ... (other parts of the DocumentCreator class remain unchanged)

def add_html_content_to_docx(self, document, html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    p = None

    for elem in soup.body:  # Directly iterate over body's children to preserve document structure
        if isinstance(elem, NavigableString):
            if p is None:  # Create a new paragraph if there isn't one already
                p = document.add_paragraph()
            text = str(elem).strip()
            if text:  # Only add text that's not empty
                p.add_run(text)
        elif isinstance(elem, Tag):
            if elem.name in ['p', 'h1', 'h2', 'h3']:
                p = document.add_paragraph()
                run = p.add_run(elem.get_text(strip=True))
                self.apply_formatting(run, elem.name)
                if elem.name in ['h1', 'h2', 'h3']:
                    run.bold = True
                    p.style = document.styles['Heading ' + elem.name[1]]
                run.font.size = Pt(12)
            else:
                # Handle inline tags such as <strong>, <em>, <u> inside paragraphs
                if p is None:
                    p = document.add_paragraph()
                for content in elem.contents:
                    run = p.add_run(str(content))
                    self.apply_formatting(run, elem)

# ... (rest of the DocumentCreator class remains unchanged)
