import re
from docx import Document

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.sections = []
        self.section_contents = {}
        self.extract_sections_from_toc()
        self.extract_contents()

    def extract_sections_from_toc(self):
        # Assuming this function is implemented and populates self.sections
        pass

    def extract_contents(self):
        document = Document(self.docx_path)
        paragraphs = document.paragraphs
        current_section = None
        content_collected = False

        # Normalization function to clean section titles
        def normalize(text):
            # Remove TOC reference and any non-alphanumeric characters except for spaces
            text = re.sub(r'PAGEREF _Toc\d+ \\h \d+', '', text)
            text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
            return re.sub(r'\s+', ' ', text).strip().lower()

        # Normalize sections for easier matching
        normalized_sections = {normalize(s): s for s in self.sections}

        for para in paragraphs:
            text = para.text.strip()
            normalized_text = normalize(text)

            # Check if the normalized text matches any normalized section title
            if normalized_text in normalized_sections:
                # Manage the collection of content under the previous section
                if current_section is not None and not content_collected:
                    self.section_contents[current_section].append("")
                current_section = normalized_sections[normalized_text]
                self.section_contents[current_section] = []
                content_collected = False
            elif current_section and text:  # Ensure non-empty paragraphs are collected
                self.section_contents[current_section].append(text)
                content_collected = True

        # Handle no content collected for the last section
        if current_section is not None and not content_collected:
            self.section_contents[current_section].append("")

    def get_sections(self):
        return self.sections

    def get_section_contents(self):
        # Format collected content into a single string per section
        return {section: '\n'.join(contents).strip() if contents else "" for section, contents in self.section_contents.items()}

# Example usage
docx_path = 'path_to_your_document.docx'  # Adjust this path
parser = DocxParser(docx_path)
print("All Sections:", parser.get_sections())
print("\nSection Contents:")
for section, content in parser.get_section_contents().items():
    print(f"Section: {section}\nContent:\n{content}\n" + "-" * 40)
