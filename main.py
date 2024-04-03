import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from io import BytesIO
from pathlib import Path
import os
 
class CustomPPTGenerator:
    def __init__(self, template=None):
        if template is None:
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
           
            req_path=os.path.join(current_script_dir,"test-utility.pptx")
           
            self.presentation = Presentation(req_path)
           
 
        else:
            self.presentation = Presentation()
        self.presentation.slide_width = Inches(13.33)  # 16:9 aspect ratio width
        self.presentation.slide_height = Inches(7.5)
        self.light_gray = RGBColor(217, 217, 217)  # 16:9 aspect ratio height
 
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
        """Adds a section to the slide with direct text content and configured text wrapping."""
        textbox = slide.shapes.add_textbox(x, y, width, height)
        textbox.fill.solid()
        textbox.fill.fore_color.rgb = self.light_gray
        text_frame = textbox.text_frame
        self.__configure_text_frame(text_frame)  # Configure text frame for wrapping
 
        # Directly add the text content
        content = self.content.get(content_key, "")
        if content:
            p = text_frame.paragraphs[0]
            run = p.add_run()
            run.text = content
            self.__configure_text_frame(text_frame)
 
    def _Layout1(self, content):
        self.content = content
        # Add a new slide with layout 6 (blank slide)
        slide = self.presentation.slides.add_slide(self.presentation.slide_layouts[6])
        # Constants
        side_margin = Inches(0.50)
        top_margin = Inches(0.53)
        bottom_margin = Inches(0.74)
        top_section_height = Inches(0.93)
        middle_section_height = Inches(5.01)
        footer_section_height = Inches(0.4)
        section_width = self.presentation.slide_width - 2 * side_margin
        footer_section_width = Inches(6.43)
        # Calculate positions for each section
        middle_section_top = (
            top_margin + top_section_height + Inches(0.24)
        )  # Border space between 1st and 2nd section
        footer_section_top = (
            self.presentation.slide_height - bottom_margin - footer_section_height
        )
        # Add sections with HTML content
        self.__add_section(
            slide, side_margin, top_margin, section_width, top_section_height, "top"
        )
        self.__add_section(
            slide,
            side_margin,
            middle_section_top,
            section_width,
            middle_section_height,
            "middle",
        )
        footer_section_left = (self.presentation.slide_width - footer_section_width) / 2
        footer_section_top = (
            self.presentation.slide_height
            - bottom_margin
            - footer_section_height
            + Inches(0.60)
        )
        self.__add_section(
            slide,
            footer_section_left,
            footer_section_top,
            footer_section_width,
            footer_section_height,
            "bottom",
        )
 
    def _Layout2(self, content):
        self.content = content
        slide = self.presentation.slides.add_slide(self.presentation.slide_layouts[6])
        # Constants for layout
        top_margin = Inches(0.53)
        bottom_space_left = Inches(0.75)
        left_right_margin = Inches(0.50)
        space_between_top_middle = Inches(0.35)
        space_between_middle_boxes = Inches(0.16)
        section_width = self.presentation.slide_width - 2 * left_right_margin
 
        # Calculate positions for each section
        middle_section_top = top_margin + Inches(0.93) + space_between_top_middle
        right_middle_left = left_right_margin + Inches(6.1) + space_between_middle_boxes
        bottom_box_y = (
            self.presentation.slide_height
            - bottom_space_left
            + (bottom_space_left - Inches(0.4)) / 2
        )
 
        # Add sections
        self.__add_section(
            slide, left_right_margin, top_margin, section_width, Inches(0.93), "top"
        )
        self.__add_section(
            slide,
            left_right_margin,
            middle_section_top,
            Inches(6.1),
            Inches(4.95),
            "middle_left",
        )
        self.__add_section(
            slide,
            right_middle_left,
            middle_section_top,
            Inches(6.1),
            Inches(4.95),
            "middle_right",
        )
        self.__add_section(
            slide,
            (self.presentation.slide_width - Inches(6.43)) / 2,
            bottom_box_y,
            Inches(6.43),
            Inches(0.4),
            "bottom",
        )
 
    def _Layout3(self, content):
        self.content = content
 
        # Add a new slide with layout 6 (blank slide)
        slide = self.presentation.slides.add_slide(self.presentation.slide_layouts[6])
 
        # Constants for layout
        side_margin = Inches(0.92)
        top_margin = Inches(0.4)
        bottom_margin = Inches(0.74)
        border_space = Inches(0.28)
        border_between_sections = Inches(0.15)
        top_section_height = Inches(1.45)
        bottom_section_height = Inches(0.4)
        middle_section_height = Inches(4.76)
        top_section_width = self.presentation.slide_width - 2 * side_margin
        bottom_section_width = Inches(6.43)
        middle_section_width_2_4 = Inches(3.77)
        middle_section_width_3 = Inches(3.39)
 
        # Add sections with HTML content
        self.__add_section(
            slide, side_margin, top_margin, top_section_width, top_section_height, "top"
        )
        # Calculate positions for middle sections
        middle_sections_top = top_margin + top_section_height + border_between_sections
        section_2_left = side_margin
        section_3_left = section_2_left + middle_section_width_2_4 + border_space
        section_4_left = section_3_left + middle_section_width_3 + border_space
        # Add middle sections with HTML content
        self.__add_section(
            slide,
            section_2_left,
            middle_sections_top,
            middle_section_width_2_4,
            middle_section_height,
            "middle_left",
        )
        self.__add_section(
            slide,
            section_3_left,
            middle_sections_top,
            middle_section_width_3,
            middle_section_height,
            "middle_center",
        )
        self.__add_section(
            slide,
            section_4_left,
            middle_sections_top,
            middle_section_width_2_4,
            middle_section_height,
            "middle_right",
        )
        # Add bottom section, centered horizontally
        bottom_section_left = (self.presentation.slide_width - bottom_section_width) / 2
        bottom_section_top = (
            self.presentation.slide_height
            - bottom_margin
            - bottom_section_height
            + Inches(0.60)
        )
        self.__add_section(
            slide,
            bottom_section_left,
            bottom_section_top,
            bottom_section_width,
            bottom_section_height,
            "bottom",
        )
 
    def _Layout4(self, content):
        self.content = (
            content  # Store content in an instance variable for access in add_section
        )
 
        # Add a new slide with layout 6 (blank slide)
        slide = self.presentation.slides.add_slide(self.presentation.slide_layouts[6])
 
        # Constants
        side_margin = Inches(0.92)
        top_margin = Inches(0.4)
        bottom_margin = Inches(1.29)
        section_width = Inches(11.5)
        section_1_height = Inches(0.72)
        section_2_height = Inches(1.45)
        section_3_height = section_2_height  # Same as section 2
        section_4_height = section_3_height  # Same as section 3
        section_5_width = Inches(6.43)
        section_5_height = Inches(0.4)
        border_1_2 = Inches(0.34)
        border_2_3 = Inches(0.19)
        border_3_4 = border_2_3  # Same as border between 2 and 3
 
        # Calculate Y positions based on heights and borders
        y_positions = [top_margin]
        heights = [
            section_1_height,
            section_2_height,
            section_3_height,
            section_4_height,
        ]
        borders = [border_1_2, border_2_3, border_3_4]
        for i, height in enumerate(heights[:-1]):
            y_positions.append(y_positions[i] + height + borders[i])
 
        # Add sections 1 to 4 with HTML content
        section_keys = ["top", "middle_top", "middle_center", "middle_bottom"]
        for i, (y, height) in enumerate(zip(y_positions, heights)):
            self.__add_section(
                slide, side_margin, y, section_width, height, section_keys[i]
            )
 
        # Add section 5 (Footer) with HTML content
        footer_y = (
            self.presentation.slide_height
            - bottom_margin
            - section_5_height
            + Inches(1.14)
        )
        footer_x = (self.presentation.slide_width - section_5_width) / 2
        self.__add_section(
            slide, footer_x, footer_y, section_5_width, section_5_height, "bottom"
        )
 
    def _Layout5(self, content):
        self.content = content
        slide = self.presentation.slides.add_slide(self.presentation.slide_layouts[6])
 
        # Constants
        left_margin = Inches(0.92)
        top_margin = Inches(0.53)
        bottom_margin = Inches(1.08)
        spacing_left_sections = Inches(0.14)
        spacing_left_right = Inches(0.4)
        footer_height = Inches(0.4)
        footer_width = Inches(6.43)
        left_section_1_height = Inches(1.91)
        left_section_2_height = Inches(3.87)
        right_section_height = Inches(5.91)
 
        # Calculate positions and add sections with text
        left_section_1_y = top_margin
        left_section_2_y = (
            left_section_1_y + left_section_1_height + spacing_left_sections
        )
        right_section_y = top_margin
        # Calculate the footer position based on the bottom margin and the spacing
        footer_y = (
            self.presentation.slide_height
            - bottom_margin
            + (bottom_margin - footer_height) / 2
            + Inches(0.15)
        )
 
        # Using add_section to add sections with HTML content
        self.__add_section(
            slide,
            left_margin,
            left_section_1_y,
            Inches(4.3),
            left_section_1_height,
            "top",
        )
        self.__add_section(
            slide,
            left_margin,
            left_section_2_y,
            Inches(4.3),
            left_section_2_height,
            "left",
        )
        self.__add_section(
            slide,
            left_margin + Inches(4.3) + spacing_left_right,
            right_section_y,
            Inches(6.75),
            right_section_height,
            "right",
        )
        self.__add_section(
            slide,
            (self.presentation.slide_width - footer_width) / 2,
            footer_y,
            footer_width,
            footer_height,
            "bottom",
        )
 
    def _generate_slide(self, layout_name, content):
        if layout_name == "Layout2":
            print(f"Generating slide for layout: {layout_name}")
            self._Layout2(content)
        elif layout_name == "Layout3":
            print(f"Generating slide for layout: {layout_name}")
            self._Layout3(content)
        elif layout_name == "Layout4":
            print(f"Generating slide for layout: {layout_name}")
            self._Layout4(content)
        elif layout_name == "Layout1":
            print(f"Generating slide for layout: {layout_name}")
            self._Layout1(content)
        elif layout_name == "Layout5":
            print(f"Generating slide for layout: {layout_name}")
            self._Layout5(content)
 
    def _validate_json(self, json_data):
        required_keys = ["layout", "content"]
        for slide_info in json_data:
            if not all(key in slide_info for key in required_keys):
                return False
            if slide_info["layout"] not in [
                "Layout3",
                "Layout4",
                "Layout2",
                "Layout1",
                "Layout5",
            ]:
                return False
        return True
 
    def generate_presentation(self, json_input):
        try:
            json_data = json.loads(json_input)
            if not self._validate_json(json_data):
                print("Invalid JSON input.")
                return
 
            for slide_info in json_data:
                layout_name = "_" + slide_info.get("layout", "")
                content = slide_info.get("content", {})
                if hasattr(self, layout_name):
                    print(f"Processing layout: {layout_name}")
                    try:
                        getattr(self, layout_name)(content)
                        print(f"Successfully generated layout: {layout_name}")
                    except Exception as e:
                        print(f"Failed to generate layout: {layout_name}. Error: {e}")
                else:
                    print(
                        f"Layout '{layout_name}' is not recognized or not implemented."
                    )
            ppt_output = BytesIO()
            self.presentation.save(ppt_output)
            ppt_output.seek(0)
            return ppt_output
 
        except json.JSONDecodeError as e:
            raise (f"Failed to decode JSON: {e}")
        except Exception as e:
            raise (f"An error occurred during presentation generation: {e}")
 
