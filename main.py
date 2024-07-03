import zipfile
import re
from lxml import etree
from docx import Document

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.sections = []
        self.section_contents = {}
        self.page_map = {}
        self.parse_docx()

    def parse_docx(self):
        self.sections = self.get_toc_sections()
        self.page_map = self.get_page_map()
        self.extract_section_contents()

    def get_toc_sections(self):
        # Open the docx file as a zip archive
        with zipfile.ZipFile(self.docx_path) as docx:
            # Read the document.xml file
            xml_content = docx.read('word/document.xml')
        
        # Parse the XML content
        tree = etree.XML(xml_content)
        
        toc_entries = []
        toc_section_pattern = re.compile(r'^\d+(\.\d+)*\s.*\s\d+$')
        found_toc = False

        for elem in tree.iter():
            if 'instrText' in elem.tag and 'TOC' in ''.join(elem.itertext()):
                found_toc = True
            elif found_toc and elem.tag.endswith('}p'):
                text = ''.join(elem.itertext()).strip()
                if toc_section_pattern.match(text):
                    # Extract section title and page number
                    match = re.match(r'^(.*\d+(\.\d+)*)\s(.*)\s(\d+)$', text)
                    section_title = match.group(3)
                    page_number = int(match.group(4))
                    toc_entries.append((section_title, page_number))
                if 'HYPERLINK' in text:
                    break
        
        return toc_entries

    def get_page_map(self):
        # Open the docx file as a zip archive
        with zipfile.ZipFile(self.docx_path) as docx:
            # Read the document.xml file
            xml_content = docx.read('word/document.xml')
        
        # Parse the XML content
        tree = etree.XML(xml_content)
        page_map = {}
        current_page = 1

        for elem in tree.iter():
            if 'lastRenderedPageBreak' in elem.tag:
                current_page += 1
            if elem.tag.endswith('}p'):
                text = ''.join(elem.itertext()).strip()
                if text and text not in page_map:
                    page_map[text] = current_page
        
        return page_map

    def extract_section_contents(self):
        document = Document(self.docx_path)
        for section, start_page in self.sections:
            self.section_contents[section] = []
            collecting = False
            for paragraph in document.paragraphs:
                text = paragraph.text.strip()
                if text in self.page_map:
                    current_page = self.page_map[text]
                    if current_page == start_page:
                        collecting = True
                    elif current_page > start_page:
                        collecting = False
                        break
                if collecting:
                    self.section_contents[section].append(paragraph.text)

    def get_sections(self):
        return [section for section, _ in self.sections]

    def get_section_contents(self):
        return [(section, '\n'.join(content).strip()) for section, content in self.section_contents.items()]

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
