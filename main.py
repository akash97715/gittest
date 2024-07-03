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
        try:
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
                    section_title = ''.join([e for e in elem.itertext()]).strip()
                    if section_title and section_title not in self.sections:
                        self.sections.append(section_title)
                        self.section_contents[section_title] = []
        except Exception as e:
            print(f"Failed in extract_sections_from_toc with error: {e}")

    def extract_contents(self):
        try:
            document = Document(self.docx_path)
            paragraphs = document.paragraphs
            print(f"Number of paragraphs: {len(paragraphs)}")  # Debugging print

            current_section = None

            for para in paragraphs:
                text = para.text.strip()
                print(f"Paragraph text: {text}")  # Debugging print
                if any(section == text for section in self.sections):
                    current_section = text
                elif current_section:
                    self.section_contents[current_section].append(text)
                    if para.style.name.startswith('Heading'):
                        if any(section == para.text.strip() for section in self.sections):
                            current_section = None
        except Exception as e:
            print(f"Failed in extract_contents with error: {e}")

        for section in self.sections:
            if not self.section_contents[section]:
                self.section_contents[section] = [""]

    def get_sections(self):
        return self.sections

    def get_section_contents(self):
        return [(section, '\n'.join(content).strip()) for section, content in self.section_contents.items()]

# Example usage
docx_path = '/path/to/your/file/B7471026 Clinical Protocol 08 Apr 2021.docx'
parser = DocxParser(docx_path)

# Get all sections
all_sections = parser.get_sections()
print("All Sections:", all_sections)

# Get contents of all sections
all_section_contents = parser.get_section_contents()
for section, content in all_section_contents:
    print(f"Section: {section}\nContent:\n{content}\n" + "-"*40)
