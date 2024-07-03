import zipfile
import re
from lxml import etree
from docx import Document

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.sections = []
        self.section_contents = {}
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
        hyperlink_pattern = re.compile(r'HYPERLINK')

        for elem in tree.iter():
            if 'instrText' in elem.tag and hyperlink_pattern.search(''.join(elem.itertext())):
                text = ''.join(elem.itertext()).strip()
                if text:
                    toc_entries.append(text)
        
        return toc_entries

    def extract_section_contents(self):
        document = Document(self.docx_path)
        current_section = None
        section_pattern = re.compile(r'^\d+(\.\d+)*\s.*$')

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()
            if text in self.sections:
                current_section = text
                self.section_contents[current_section] = []
            if current_section:
                self.section_contents[current_section].append(paragraph.text)

        # Convert the contents to a list of tuples
        self.section_contents = [(section, '\n'.join(content).strip()) for section, content in self.section_contents.items()]

    def get_sections(self):
        return self.sections

    def get_section_contents(self):
        return self.section_contents

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
