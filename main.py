from docx import Document
import re

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.toc = []
        self.sections = {}
        self.extract_toc_and_contents()

    def extract_toc_and_contents(self):
        document = Document(self.docx_path)
        toc_started = False

        for para in document.paragraphs:
            if para.style.name.startswith('Heading 1') and not toc_started:
                toc_started = True
            if toc_started:
                if para.style.name.startswith('Heading'):
                    section_title = para.text.strip()
                    self.toc.append(section_title)
                    self.sections[section_title] = []
                elif para.style.name == 'Normal' and self.toc:
                    self.sections[self.toc[-1]].append(para.text.strip())

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
