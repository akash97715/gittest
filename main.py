import zipfile
from lxml import etree
from docx import Document

def get_toc_entries(docx_path):
    # Open the docx file as a zip archive
    with zipfile.ZipFile(docx_path) as docx:
        # Read the document.xml file
        xml_content = docx.read('word/document.xml')
    
    # Parse the XML content
    tree = etree.XML(xml_content)
    
    toc_entries = []
    found_toc = False

    for elem in tree.iter():
        if 'fldSimple' in elem.tag or 'instrText' in elem.tag:
            if 'TOC' in ''.join(elem.itertext()):
                found_toc = True
        elif found_toc and elem.tag.endswith('}p'):
            # Collect TOC entries
            text = ''.join(elem.itertext()).strip()
            if text:
                toc_entries.append(text)
            # Check for the end of TOC
            if 'HYPERLINK' in text:
                break

    return toc_entries

def extract_sections_from_docx(docx_path):
    document = Document(docx_path)
    toc_entries = get_toc_entries(docx_path)
    sections = []

    # Extract section titles from TOC entries
    for entry in toc_entries:
        sections.append(entry)

    # Extract content based on sections
    section_texts = {section: [] for section in sections}
    current_section = None

    for paragraph in document.paragraphs:
        if paragraph.text.strip() in sections:
            current_section = paragraph.text.strip()
        if current_section:
            section_texts[current_section].append(paragraph.text)

    # Convert section texts to a list of lists
    section_content_list = [section_texts[section] for section in sections]

    return section_content_list

# Example usage
docx_path = 'path_to_your_docx_file.docx'
section_contents = extract_sections_from_docx(docx_path)

for index, section in enumerate(section_contents):
    print(f"Section {index + 1} Content:")
    print("\n".join(section))
    print("\n" + "-"*40 + "\n")
