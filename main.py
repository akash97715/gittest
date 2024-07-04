import re
import json
from PyPDF2 import PdfFileReader

def extract_text(pdf_file, page_numbers=None):
    # Dummy implementation of text extraction from PDF. Replace with actual implementation.
    return """
    Table of Contents
    1. INTRODUCTION ........................................................................... 1
    2. STUDY OBJECTIVES, ENDPOINTS AND ESTIMANDS.................... 3
    3. INVESTIGATIONAL PLAN ............................................................ 19
    4. STUDY PARTICIPANTS ................................................................. 28
    5. EVALUATION OF RESPONSE TO STUDY INTERVENTION ............ 44
    6. CONCLUSIONS ............................................................................. 76
    7. REFERENCES ................................................................................. 78
    """

def format_table_of_contents(table_of_contents):
    formatted = []
    for entry in table_of_contents:
        section = re.match(r'^\d+(\.\d+)*', entry).group()
        title = re.search(r'([A-Z][A-Z ]+)', entry).group().strip()
        page = re.search(r'\d+$', entry).group()
        formatted.append({'section': section, 'title': title, 'page': page})
    return formatted

def extract_table_of_contents(file_path):
    """
    Extracts the table of contents from a PDF file and saves it as JSON.
    :param file_path: Path to the PDF file.
    """
    logger.info("extracting table of content")
   
    text = extract_text(pdf_file=file_path, page_numbers=[i for i in range(11)])
   
    lines = text.split("\n")
    lines = [line.rstrip() for line in lines if line.strip()]
    table_of_contents = []
 
    # Updated regex pattern to capture the TOC lines
    toc_regex = re.compile(r'^\d+(\.\d+)*\.\s+.*\s+\.{3,}\s*\d+$')
    print("toc_regex", lines)
 
    for line_num in range(len(lines) - 1):
        line = lines[line_num]
        if not line[-1].isdigit() and lines[line_num + 1][0].isdigit():
            line += " " + lines[line_num + 1]
        
        match = toc_regex.match(line)
        if match:
            table_of_contents.append(line.strip())
 
    print("table_of_contents", table_of_contents)
 
    if len(table_of_contents) == 0:
        raise InvalidPdfException(data=file_path.split("/")[-1])
 
    section_headings = format_table_of_contents(table_of_contents)
 
    return section_headings

# Assuming logger and InvalidPdfException are defined somewhere in the complete code

# Test the function
file_path = 'sample.pdf'
try:
    toc = extract_table_of_contents(file_path)
    print(json.dumps(toc, indent=2))
except InvalidPdfException as e:
    print(f"Failed to extract table of contents: {e}")
