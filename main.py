from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape

def draw_text(pdf_canvas, text, x, y, font_size=12):
    pdf_canvas.setFont("Helvetica", font_size)
    text_object = pdf_canvas.beginText(x, y)
    text_object.textLine(text)
    pdf_canvas.drawText(text_object)

def pptx_to_pdf(pptx_path, pdf_path):
    prs = Presentation(pptx_path)
    pdf_canvas = canvas.Canvas(pdf_path, pagesize=landscape(letter))
    
    for slide_number, slide in enumerate(prs.slides):
        # Define initial Y position for text
        y_position = landscape(letter)[1] - 40  # Start from top of the page
        
        for shape in slide.shapes:
            if hasattr(shape, "text_frame") and shape.text_frame is not None:
                for paragraph in shape.text_frame.paragraphs:
                    text = "".join([run.text for run in paragraph.runs])
                    if text.strip():  # Check if there is any text to draw
                        draw_text(pdf_canvas, text, 40, y_position, font_size=12)
                        y_position -= 20  # Move to the next line
                        
                        if y_position < 40:  # Check if Y position is out of the page
                            pdf_canvas.showPage()  # Add a new page
                            y_position = landscape(letter)[1] - 40  # Reset Y position for new page
        
        pdf_canvas.showPage()  # Add a new page for each slide
    
    pdf_canvas.save()

pptx_path = 'your_presentation.pptx'
pdf_path = 'output.pdf'
pptx_to_pdf(pptx_path, pdf_path)
