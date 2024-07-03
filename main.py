    def extract_sections_from_toc(self):
        document = Document(self.docx_path)
        for para in document.paragraphs:
            if para.style.name.startswith('Heading'):
                normalized_title = para.text.strip()
                if normalized_title not in self.sections:
                    self.sections.append(normalized_title)
                    self.section_contents[normalized_title] = []
