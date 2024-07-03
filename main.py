import fitz  # PyMuPDF

class CustomPdfParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.sections = []
        self.section_contents = {}
        self.extract_sections_from_pdf()

    def extract_sections_from_pdf(self):
        document = fitz.open(self.pdf_path)
        current_section = None
        for page in document:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if 'lines' in block:
                    for line in block['lines']:
                        for span in line['spans']:
                            text = span['text'].strip()
                            if self.is_section_header(text, span):
                                if text not in self.sections:
                                    self.sections.append(text)
                                    self.section_contents[text] = []
                                current_section = text
                            elif current_section:
                                self.section_contents[current_section].append(text)

        # Combine texts for each section
        for key in self.section_contents.keys():
            self.section_contents[key] = "\n".join(self.section_contents[key])

    def is_section_header(self, text, span):
        # Define rules to identify section headers, e.g., font size, bold text
        # This is a simple heuristic: assuming headers are in bold and larger font
        return span['flags'] == 20 and span['size'] > 12

# Example usage
pdf_path = 'path_to_your_document.pdf'  # Adjust this path
parser = CustomPdfParser(pdf_path)
print("Sections Found:", parser.sections)
for section, content in parser.section_contents.items():
    print(f"Section: {section}\nContent:\n{content}\n" + "-" * 40)
