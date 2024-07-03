from docx import Document
from lxml import etree
import zipfile

def get_toc_paragraphs(docx_path):
    with zipfile.ZipFile(docx_path) as docx:
        xml_content = docx.read('word/document.xml')
    tree = etree.XML(xml_content)

    toc_paragraphs = []
    for elem in tree.iter():
        if 'fldSimple' in elem.tag or 'instrText' in elem.tag:
            if 'TOC' in etree.tostring(elem, encoding='unicode'):
                while elem is not None:
                    if elem.tag.endswith('}p'):
                        toc_paragraphs.append(elem)
                    elem = elem.getnext()
                break

    return toc_paragraphs

def extract_sections_from_docx(docx_path):
    document = Document(docx_path)
    toc_paragraphs = get_toc_paragraphs(docx_path)
    sections = []

    # Extract section titles from TOC paragraphs
    for para in toc_paragraphs:
        text = ''.join(para.itertext()).strip()
        if text:
            sections.append(text)

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
