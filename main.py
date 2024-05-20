from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import io

def pptx_to_pdf(pptx_path, pdf_path):
    prs = Presentation(pptx_path)
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=letter)

    for slide_number, slide in enumerate(prs.slides):
        # Create a blank image to draw the slide on
        slide_image = Image.new('RGB', (int(letter[0]), int(letter[1])), 'white')
        slide_io = io.BytesIO()
        slide_image.save(slide_io, format='PNG')
        slide_io.seek(0)
        
        # Draw slide content
        pdf_canvas.drawImage(slide_io, 0, 0, width=letter[0], height=letter[1])

        if slide_number < len(prs.slides) - 1:
            pdf_canvas.showPage()

    pdf_canvas.save()

pptx_path = 'your_presentation.pptx'
pdf_path = 'output.pdf'
pptx_to_pdf(pptx_path, pdf_path)
