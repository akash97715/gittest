from docx import Document
import re

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.toc = []
        self.sections = {}
        self.extract_toc()
        self.extract_contents()

    def extract_toc(self):
        document = Document(self.docx_path)
        toc_started = False

        for para in document.paragraphs:
            if 'Table of Contents' in para.text:
                toc_started = True
                continue
            if toc_started:
                if para.style.name.startswith('Heading'):
                    section_title = para.text.strip()
                    self.toc.append(section_title)
                    self.sections[section_title] = []

    def extract_contents(self):
        document = Document(self.docx_path)
        current_section = None

        for para in document.paragraphs:
            text = para.text.strip()
            if text in self.toc:
                current_section = text
            if current_section:
                self.sections[current_section].append(para.text.strip())

        # Remove empty content lists and ensure each section has at least an empty string as content
        for section in self.sections:
            self.sections[section] = [p for p in self.sections[section] if p]
            if not self.sections[section]:
                self.sections[section] = [""]

    def get_sections(self):
        return self.toc

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
