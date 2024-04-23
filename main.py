path="tobeingest/figures"
def encode_image(image_path):
    ''' Getting the base64 string '''
    with open(image_path, "rb") as image_file:
 
        return base64.b64encode(image_file.read()).decode('utf-8')
# Store base64 encoded images
img_base64_list = []
 
# Store image summaries
image_summaries = []
for img_file in sorted(os.listdir(path)):
    if img_file.endswith('.jpg'):
        img_path = os.path.join(path, img_file)
        base64_image = encode_image(img_path)
        img_base64_list.append(base64_image)
        image_summaries.append(image_summarize(base64_image,prompt))


[{'document_name': 'tobeingest',  'figure_id': 'd02607d7-4682-4169-b54a-90616e997467',  'figure_name': 'page_6_figure_1.jpg',  'figure_page': 6,  'figure_confidence': 0.6298828125,  'figure_bbox': x: 0.20833560824394226, y: 0.8161853551864624, width: 0.197014681994915, height: 0.0221949340775609,  'figure_height': 0.0221949340775609,  'figure_width': 0.197014681994915,  'figure_x': 0.20833560824394226,  'figure_y': 0.8161853551864624,  'figure_path': 'tobeingest\\figures\\page_6_figure_1.jpg'}, {'document_name': 'tobeingest',  'figure_id': '225885e9-7277-4354-be7d-fd99a6bac1e5',  'figure_name': 'page_6_figure_2.jpg',  'figure_page': 6,  'figure_confidence': 0.82958984375,  'figure_bbox': x: 0.48349881172180176, y: 0.6204254031181335, width: 0.4356090724468231, height: 0.21089325845241547,  'figure_height': 0.21089325845241547,  'figure_width': 0.4356090724468231,  'figure_x': 0.48349881172180176,  'figure_y': 0.6204254031181335,  'figure_path': 'tobeingest\\figures\\page_6_figure_2.jpg'},
