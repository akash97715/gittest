import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from io import BytesIO
import os

class CustomPPTGenerator:
    def __init__(self, template=None):
        if template is None:
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
            req_path = os.path.join(current_script_dir, "test-utility.pptx")
            self.presentation = Presentation(req_path)
        else:
            self.presentation = Presentation()
        self.presentation.slide_width = Inches(13.33)  # 16:9 aspect ratio width
        self.presentation.slide_height = Inches(7.5)
        self.light_gray = RGBColor(255, 255, 255)  # Changed to white

    def __configure_text_frame(self, text_frame):
        """Configure a text frame to ensure proper text wrapping and aesthetics."""
        text_frame.word_wrap = True
        text_frame.auto_size = True
        text_frame.margin_left = Pt(10)
        text_frame.margin_top = Pt(10)
        text_frame.margin_right = Pt(10)
        text_frame.margin_bottom = Pt(10)

        for paragraph in text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = "sans-serif"
                run.font.size = Pt(12)

    def __add_section(self, slide, x, y, width, height, content_key):
        """Adds a section to the slide with direct text content, configured text wrapping, and a thick black border."""
        textbox = slide.shapes.add_textbox(x, y, width, height)
        textbox.fill.solid()
        textbox.fill.fore_color.rgb = self.light_gray
        text_frame = textbox.text_frame
        self.__configure_text_frame(text_frame)  # Configure text frame for wrapping

        # Set a thick black border for the textbox
        textbox.line.color.rgb = RGBColor(0, 0, 0)  # Black
        textbox.line.width = Pt(2)  # Adjust the border thickness as desired

        # Directly add the text content
        content = self.content.get(content_key, "")
        if content:
            p = text_frame.paragraphs[0]
            run = p.add_run()
            run.text = content
            self.__configure_text_frame(text_frame)

    # The rest of the class remains unchanged...
