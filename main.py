    def __init__(self, template=None):
        if template is None:
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
           
            req_path=os.path.join(current_script_dir,"test-utility.pptx")
           
            self.presentation = Presentation(req_path)
           
 
        else:
            self.presentation = Presentation()
        self.presentation.slide_width = Inches(13.33)  # 16:9 aspect ratio width
        self.presentation.slide_height = Inches(7.5)
        self.light_gray = RGBColor(217, 217, 217)
