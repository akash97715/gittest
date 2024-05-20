from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

class PptxToPdfConverter:
    def __init__(self, pptx_path, pdf_path):
        self.pptx_path = pptx_path
        self.pdf_path = pdf_path

    def draw_text(self, pdf_canvas, text, x, y, font_size=12):
        pdf_canvas.setFont("Helvetica", font_size)
        text_object = pdf_canvas.beginText(x, y)
        text_object.textLine(text)
        pdf_canvas.drawText(text_object)

    def draw_image(self, pdf_canvas, image, x, y, width, height):
        pdf_canvas.drawImage(ImageReader(image), x, y, width=width, height=height)

    def extract_images(self, shape):
        image_stream = io.BytesIO(shape.image.blob)
        image = Image.open(image_stream)
        return image

    def pptx_to_pdf(self):
        prs = Presentation(self.pptx_path)
        pdf_canvas = canvas.Canvas(self.pdf_path, pagesize=landscape(letter))
        
        for slide_number, slide in enumerate(prs.slides):
            y_position = landscape(letter)[1] - 40  # Start from top of the page

            for shape in slide.shapes:
                if hasattr(shape, "text_frame") and shape.text_frame is not None:
                    for paragraph in shape.text_frame.paragraphs:
                        text = "".join([run.text for run in paragraph.runs])
                        if text.strip():  # Check if there is any text to draw
                            self.draw_text(pdf_canvas, text, 40, y_position, font_size=12)
                            y_position -= 20  # Move to the next line

                            if y_position < 40:  # Check if Y position is out of the page
                                pdf_canvas.showPage()  # Add a new page
                                y_position = landscape(letter)[1] - 40  # Reset Y position for new page
                
                if hasattr(shape, "image"):
                    image = self.extract_images(shape)
                    img_width, img_height = image.size
                    aspect_ratio = img_height / img_width
                    img_width_pdf = 400  # Arbitrary width to fit the image
                    img_height_pdf = img_width_pdf * aspect_ratio
                    self.draw_image(pdf_canvas, image, 40, y_position - img_height_pdf, width=img_width_pdf, height=img_height_pdf)
                    y_position -= img_height_pdf + 20  # Adjust y_position after drawing the image

                    if y_position < 40:  # Check if Y position is out of the page
                        pdf_canvas.showPage()  # Add a new page
                        y_position = landscape(letter)[1] - 40  # Reset Y position for new page

            pdf_canvas.showPage()  # Add a new page for each slide
        
        pdf_canvas.save()

# Example usage
pptx_path = 'your_presentation.pptx'
pdf_path = 'output.pdf'
converter = PptxToPdfConverter(pptx_path, pdf_path)
converter.pptx_to_pdf()
