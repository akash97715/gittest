import zipfile
import re
from lxml import etree
from docx import Document

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.sections = {}
        self.parse_docx()

    def parse_docx(self):
        self.sections = self.get_toc_sections()
        self.extract_section_contents()

    def get_toc_sections(self):
        # Open the docx file as a zip archive
        with zipfile.ZipFile(self.docx_path) as docx:
            # Read the document.xml file
            xml_content = docx.read('word/document.xml')
        
        # Parse the XML content
        tree = etree.XML(xml_content)
        
        toc_entries = []
        toc_section_pattern = re.compile(r'^\d+(\.\d+)*\s.*\d+$')
        found_toc = False

        for elem in tree.iter():
            if 'fldSimple' in elem.tag or 'instrText' in elem.tag:
                if 'TOC' in ''.join(elem.itertext()):
                    found_toc = True
            elif found_toc and elem.tag.endswith('}p'):
                text = ''.join(elem.itertext()).strip()
                if toc_section_pattern.match(text):
                    # Remove page number from the TOC entry
                    section_title = re.sub(r'\s\d+$', '', text)
                    toc_entries.append(section_title)
                # Check for the end of TOC
                if 'HYPERLINK' in text:
                    break
        
        sections = {entry: [] for entry in toc_entries}
        return sections

    def extract_section_contents(self):
        document = Document(self.docx_path)
        current_section = None
        section_pattern = re.compile(r'^\d+(\.\d+)*\s.*$')

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()
            if section_pattern.match(text):
                if text in self.sections:
                    current_section = text
            if current_section:
                self.sections[current_section].append(paragraph.text)

    def get_sections(self):
        return list(self.sections.keys())

    def get_section_contents(self):
        return [(section, '\n'.join(content).strip()) for section, content in self.sections.items()]

# Example usage
docx_path = 'path_to_your_docx_file.docx'
parser = DocxParser(docx_path)

# Get all sections
all_sections = parser.get_sections()
print("All Sections:", all_sections)

# Get contents of all sections
all_section_contents = parser.get_section_contents()
for section, content in all_section_contents:
    print(f"Section: {section}")
    print(f"Content:\n{content}")
    print("\n" + "-"*40 + "\n")
