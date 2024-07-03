import zipfile
import re
from lxml import etree
from docx import Document

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.sections = {}
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
            if 'instrText' in elem.tag:
                if 'TOC' in ''.join(elem.itertext()):
                    found_toc = True
            elif found_toc and elem.tag.endswith('}p'):
                text = ''.join(elem.itertext()).strip()
                if toc_section_pattern.match(text):
                    # Extract section title and page number
                    section_title = re.sub(r'\s\d+$', '', text)
                    page_number = re.findall(r'\d+$', text)[0]
                    toc_entries.append((section_title, int(page_number)))
                # Check for the end of TOC
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
                if text:
                    if text not in page_map:
                        page_map[text] = current_page
        
        return page_map

    def extract_section_contents(self):
        document = Document(self.docx_path)
        section_content = {}
        for section, start_page in self.sections:
            section_content[section] = []
            for paragraph in document.paragraphs:
                text = paragraph.text.strip()
                if text in self.page_map and self.page_map[text] >= start_page:
                    section_content[section].append(paragraph.text)
                    if self.sections.index((section, start_page)) + 1 < len(self.sections):
                        end_page = self.sections[self.sections.index((section, start_page)) + 1][1]
                        if self.page_map[text] >= end_page:
                            break
        self.sections = section_content

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
