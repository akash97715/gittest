from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io

def pptx_to_pdf(pptx_path, pdf_path):
    prs = Presentation(pptx_path)
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=letter)
    
    for slide_number, slide in enumerate(prs.slides):
        slide_image = Image.new('RGB', (int(letter[0]), int(letter[1])), 'white')
        slide_io = io.BytesIO()
        slide_image.save(slide_io, format='PNG')
        slide_io.seek(0)

        # Convert slide to image using PIL
        img = Image.open(slide_io)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Draw the slide image on the PDF canvas
        pdf_canvas.drawImage(ImageReader(img_byte_arr), 0, 0, width=letter[0], height=letter[1])

        if slide_number < len(prs.slides) - 1:
            pdf_canvas.showPage()
    
    pdf_canvas.save()

pptx_path = 'your_presentation.pptx'
pdf_path = 'output.pdf'
pptx_to_pdf(pptx_path, pdf_path)
