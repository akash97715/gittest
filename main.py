from docx import Document

class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.sections = []
        self.section_contents = {}
        self.extract_sections_from_toc()
        self.extract_contents()

    def extract_sections_from_toc(self):
        # Assuming this function fills self.sections with correct titles including any PAGEREF details
        pass

    def extract_contents(self):
        document = Document(self.docx_path)
        paragraphs = document.paragraphs
        current_section = None
        content_collected = False

        # Define a function to normalize text by removing non-alphanumeric characters and PAGEREF info
        def normalize(text):
            import re
            # Remove PAGEREF and any non-alphanumeric characters except for spaces
            text = re.sub(r'PAGEREF _Toc\d+ \\h \d+', '', text)
            text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
            return text.strip().lower()

        # Normalize sections for easier matching
        normalized_sections = {normalize(s): s for s in self.sections}

        for para in paragraphs:
            text = para.text.strip()
            normalized_text = normalize(text)

            # Check if the normalized text matches any normalized section title
            if normalized_text in normalized_sections:
                if current_section is not None and not content_collected:
                    # Assign blank if no content was found for the previous section
                    self.section_contents[current_section].append("")
                current_section = normalized_sections[normalized_text]
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
        return {section: '\n'.join(contents).strip() if contents else "" for section, contents in self.section_contents.items()}

# Example usage
docx_path = '/path/to/your/docx/file.docx'  # Adjust the path accordingly
parser = DocxParser(docx_path)

# Get all sections
all_sections = parser.get_sections()
print("All Sections:", all_sections)

# Get contents of all sections
all_section_contents = parser.get_section_contents()
for section, content in all_section_contents.items():
    print(f"Section: {section}\nContent:\n{content}\n" + "-"*40)
