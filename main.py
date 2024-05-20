from pptx2pdf import convert

def pptx_to_pdf(pptx_path, pdf_path):
    convert(pptx_path, outputfile=pdf_path)

pptx_path = 'your_presentation.pptx'
pdf_path = 'output.pdf'
pptx_to_pdf(pptx_path, pdf_path)
