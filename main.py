from docx import Document
import re

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.sections = []
        self.section_contents = {}
        self.extract_sections_and_contents()

    def extract_sections_and_contents(self):
        document = Document(self.docx_path)
        toc_started = False
        current_section = None
        section_pattern = re.compile(r'^\d+(\.\d+)*\s.*$')

        # First, capture sections and subsections from the TOC
        for para in document.paragraphs:
            if para.style.name.startswith('Heading 1') and not toc_started:
                toc_started = True
            if toc_started:
                if para.style.name.startswith('Heading'):
                    section_title = para.text.strip()
                    if section_pattern.match(section_title):
                        self.sections.append(section_title)
                        current_section = section_title
                        self.section_contents[current_section] = []

        # Then, extract content based on captured sections
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
            self.section_contents[section] = [p for p in self.section_contents[section] if p]
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
