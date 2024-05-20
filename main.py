from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape

def draw_text(canvas, text, x, y, font_size=12):
    canvas.setFont("Helvetica", font_size)
    text_object = canvas.beginText(x, y)
    text_object.textLine(text)
    canvas.drawText(text_object)

def pptx_to_pdf(pptx_path, pdf_path):
    prs = Presentation(pptx_path)
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=landscape(letter))
    
    for slide_number, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text_frame = shape.text_frame
                for paragraph in text_frame.paragraphs:
                    for run in paragraph.runs:
                        # You might need to adjust positioning and font size
                        draw_text(pdf_canvas, run.text, 100, 500 - slide_number * 100)
        
        if slide_number < len(prs.slides) - 1:
            pdf_canvas.showPage()
    
    pdf_canvas.save()

pptx_path = 'your_presentation.pptx'
pdf_path = 'output.pdf'
pptx_to_pdf(pptx_path, pdf_path)
