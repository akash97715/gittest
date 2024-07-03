from docx import Document

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.sections = []
        self.section_contents = {}
        self.extract_sections_from_toc()
        self.extract_contents()

    def extract_sections_from_toc(self):
        # Your existing TOC extraction logic...
        pass

    def extract_contents(self):
        document = Document(self.docx_path)
        paragraphs = document.paragraphs
        current_section = None
        content_collected = False

        for para in paragraphs:
            text = para.text.strip()
            # Check if the text is exactly a section title
            if text in self.sections:
                if current_section is not None and not content_collected:
                    # If no content was found for the previous section, assign blank
                    self.section_contents[current_section].append("")
                # Update current section
                current_section = text
                self.section_contents[current_section] = []
                content_collected = False  # Reset the content collected flag
            elif current_section:
                # Collect text under the current section
                self.section_contents[current_section].append(text)
                content_collected = True

        # After the last paragraph, check if the last section has no content
        if current_section is not None and not content_collected:
            self.section_contents[current_section].append("")

    def get_sections(self):
        return self.sections

    def get_section_contents(self):
        # Join the collected content for each section into a single string
        return {section: '\n'.join(contents).strip() for section, contents in self.section_contents.items()}

# Example usage
docx_path = '/path/to/your/docx/file.docx'
parser = DocxParser(docx_path)

# Get all sections
all_sections = parser.get_sections()
print("All Sections:", all_sections)

# Get contents of all sections
all_section_contents = parser.get_section_contents()
for section, content in all_section_contents.items():
    print(f"Section: {section}\nContent:\n{content}\n" + "-"*40)
