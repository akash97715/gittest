import zipfile
from lxml import etree
from docx import Document

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.sections = []
        self.section_contents = {}
        self.extract_sections_from_toc()
        self.extract_contents()

    def extract_sections_from_toc(self):
        with zipfile.ZipFile(self.docx_path) as docx:
            xml_content = docx.read('word/document.xml')
        tree = etree.XML(xml_content)
        
        toc_started = False
        for elem in tree.iter():
            if 'fldSimple' in elem.tag or 'instrText' in elem.tag:
                if 'TOC' in ''.join(elem.itertext()):
                    toc_started = True
                    continue
            if toc_started and elem.tag.endswith('}hyperlink'):
                for subelem in elem.iter():
                    if subelem.tag.endswith('}t'):
                        section_title = ''.join(subelem.itertext()).strip()
                        if section_title and section_title not in self.sections:
                            self.sections.append(section_title)
                            self.section_contents[section_title] = []
            if toc_started and elem.tag.endswith('}p'):
                text = ''.join(elem.itertext()).strip()
                if text in self.sections:
                    current_section = text
                if current_section:
                    self.section_contents[current_section].append(text)

    def extract_contents(self):
        document = Document(self.docx_path)
        current_section = None

        for para in document.paragraphs:
            text = para.text.strip()
            if text in self.sections:
                current_section = text
            if current_section:
                if text != current_section:  # Avoid adding the section title as content
                    self.section_contents[current_section].append(para.text.strip())

        # Remove empty content lists and ensure each section has at least an empty string as content
        for section in self.sections:
            self.section_contents[section] = [p for p in self.section_contents[section] if p and p != section]
            if not self.section_contents[section]:
                self.section_contents[section] = [""]

    def get_sections(self):
        return self.sections

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
