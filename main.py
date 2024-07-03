from docx import Document
import zipfile
from lxml import etree

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.sections = []
        self.section_contents = {}
        self.extract_sections_from_toc()

    def extract_sections_from_toc(self):
        try:
            # First attempt to extract from the XML content
            with zipfile.ZipFile(self.docx_path) as docx:
                xml_content = docx.read('word/document.xml')
            tree = etree.XML(xml_content)

            toc_started = False
            toc_found = False  # Indicator if TOC based sections are found

            for elem in tree.iter():
                if 'fldSimple' in elem.tag or 'instrText' in elem.tag:
                    if 'TOC' in ''.join(elem.itertext()):
                        toc_started = True
                        continue
                if toc_started and elem.tag.endswith('}hyperlink'):
                    section_title = ''.join(e for e in elem.itertext()).strip()
                    if section_title:
                        self.sections.append(section_title)
                        self.section_contents[section_title] = []
                        toc_found = True

            # If no sections were found using TOC, use heading styles
            if not toc_found:
                self.extract_sections_from_headings()

        except Exception as e:
            print(f"Failed to extract sections using TOC with error: {e}")
            # Fallback to extracting from headings if XML processing fails
            self.extract_sections_from_headings()

    def extract_sections_from_headings(self):
        document = Document(self.docx_path)
        for para in document.paragraphs:
            if para.style.name.startswith('Heading'):
                normalized_title = para.text.strip()
                if normalized_title and normalized_title not in self.sections:
                    self.sections.append(normalized_title)
                    self.section_contents[normalized_title] = []

# Example usage
docx_path = 'path_to_your_document.docx'  # Adjust this path
parser = DocxParser(docx_path)
print("Sections Found:", parser.sections)
