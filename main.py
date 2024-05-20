from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

def pptx_to_pdf(pptx_path, pdf_path):
    prs = Presentation(pptx_path)
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=landscape(letter))
    
    for slide_number, slide in enumerate(prs.slides):
        # Create a blank image with white background
        slide_image = Image.new('RGB', (prs.slide_width, prs.slide_height), 'white')
        slide_io = io.BytesIO()
        slide_image.save(slide_io, format='PNG')
        slide_io.seek(0)

        # Draw the slide image on the PDF canvas
        img_reader = ImageReader(slide_io)
        pdf_canvas.drawImage(img_reader, 0, 0, width=landscape(letter)[0], height=landscape(letter)[1])
        
        if slide_number < len(prs.slides) - 1:
            pdf_canvas.showPage()

    pdf_canvas.save()

pptx_path = 'your_presentation.pptx'
pdf_path = 'output.pdf'
pptx_to_pdf(pptx_path, pdf_path)
