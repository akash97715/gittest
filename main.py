from bs4 import BeautifulSoup, NavigableString
from docx import Document
from docx.shared import Pt
from io import BytesIO
import base64
from docx.oxml.shared import OxmlElement, qn
from docx.oxml.ns import qn as xml_qn

class DocumentCreator:
    def __init__(self, payload):
        self.payload = payload

    @staticmethod
    def apply_formatting(run, tag):
        if tag in ['strong', 'b']:
            run.bold = True
        if tag in ['em', 'i']:
            run.italic = True
        if tag == 'u':
            run.underline = True
        run.font.size = Pt(12)
        run.font.name = 'Arial'  # Changed to a more commonly available font

    @staticmethod
    def add_hyperlink(paragraph, url, text, tooltip=None):
        part = paragraph.part
        r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)

        hyperlink = OxmlElement('w:hyperlink')
        hyperlink.set(qn('r:id'), r_id)
        if tooltip:
            hyperlink.set(qn('w:tooltip'), tooltip)

        new_run = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')

        # Set the style to 'Hyperlink'
        style = OxmlElement('w:rStyle')
        style.set(qn('w:val'), 'Hyperlink')
        rPr.append(style)

        # Add underline
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rPr.append(u)

        new_run.append(rPr)
        new_run.text = text
        hyperlink.append(new_run)

        paragraph._p.append(hyperlink)

    @staticmethod
    def add_image(document, image_data):
        image_stream = BytesIO(base64.b64decode(image_data.split(',')[1]))
        document.add_picture(image_stream)

    @staticmethod
    def add_table(document, html_table):
        soup = BeautifulSoup(html_table, "html.parser")
        table = document.add_table(rows=0, cols=0)
        for idx, row in enumerate(soup.find_all("tr")):
            if idx == 0:
                hdr_cells = table.add_row().cells
                for th, hdr_cell in zip(row.find_all("th"), hdr_cells):
                    hdr_cell.text = th.get_text()
            else:
                row_cells = table.add_row().cells
                for td, row_cell in zip(row.find_all("td"), row_cells):
                    row_cell.text = td.get_text()

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        current_paragraph = document.add_paragraph()
        added_texts = set()

        for elem in soup.descendants:
            if isinstance(elem, NavigableString):
                text = str(elem).strip()
                if text and text not in added_texts:
                    parent = elem.parent
                    if parent.name == 'a' and parent.has_attr('href'):
                        if current_paragraph.text != '':
                            current_paragraph.add_run(' ')
                        self.add_hyperlink(current_paragraph, parent['href'], text)
                        current_paragraph.add_run(' ')
                    else:
                        run = current_paragraph.add_run(text)
                        self.apply_formatting(run, parent.name)
                    added_texts.add(text)
            elif elem.name in ['p', 'h1', 'h2', 'h3']:
                if current_paragraph.text:
                    current_paragraph = document.add_paragraph()
                for content in elem.contents:
                    if isinstance(content, NavigableString):
                        text = str(content).strip()
                        if text and text not in added_texts:
                            run = current_paragraph.add_run(text)
                            self.apply_formatting(run, elem.name)
                            added_texts.add(text)
                    elif content.name == 'a' and content.has_attr('href'):
                        text = content.get_text(strip=True)
                        if text not in added_texts:
                            if current_paragraph.text != '':
                                current_paragraph.add_run(' ')
                            self.add_hyperlink(current_paragraph, content['href'], text)
                            current_paragraph.add_run(' ')
                            added_texts.add(text)
                if elem.name in ['h1', 'h2', 'h3']:
                    current_paragraph.style = document.styles['Heading ' + elem.name[1]]

    def create_document(self):
        document = Document()
        for placeholder in self.payload['placeholders']:
            html_content = placeholder['content']['text']
            self.add_html_content_to_docx(document, html_content)

            if 'images' in placeholder['content']:
                for image_data in placeholder['content']['images']:
                    self.add_image(document, image_data)

            if 'tables' in placeholder['content']:
                for html_table in placeholder['content']['tables']:
                    self.add_table(document, html_table)

            citations = placeholder['content'].get('citations')
            if citations:
                p = document.add_paragraph("Citations:\n")
                for citation in citations:
                    source = citation['filename'] if citation['filename'].strip() else "N/A"
                    page = str(citation['page']) if str(citation['page']).strip() else "N/A"
                    section = str(citation['section']) if str(citation['section']).strip() else "N/A"
                    citation_text = f"Filename: {source}, Page: {page}, Section: {section}\n"                
                    run = p.add_run(citation_text)
                    run.font.size = Pt(8)
                    run.font.name = 'Arial'  # Ensure font is set correctly

        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob
