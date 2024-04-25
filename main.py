---------------------------------------------------------------------------OSError                                   Traceback (most recent call last)Cell In[2],
line 120
   
117
figures_doc = doc_analyzer.analyze_document([TextractFeatures.LAYOUT])   
119
#doc_analyzer.extract_figures(figures_doc)-->
120
doc_analyzer.extract_tables(tables_doc) Cell In[2],
line 51
    
49
for page in doc_object.pages:    
50
     for table in page.tables:--->
51
         self.process_table(table, page) Cell In[2],
line 57
    
55
cropped_image = self.crop_image(page.image, table.bbox, page.image.size)    
56
table_img_path = f'{self.doc_name}/tables/img/{table_name}.png'--->
57
cropped_image.save(table_img_path)    
59
table_info = self.collect_table_info(table, table_name, table_img_path)    
60
self.tables.append(table_info) File
d:\docinsightenv\Lib\site-packages\PIL\Image.py:2456
, in Image.save(self, fp, format, **params)  
2454
         fp = builtins.open(filename, "r+b")  
2455
     else:->
2456
         fp = builtins.open(filename, "w+b")  
2458
try:  
2459
     save_handler(self, fp, filename) OSError: [Errno 22] Invalid argument: 'D:\\retreiver\\s3:\\sbx-docinsight-ocr\\[II_MANU_01_OUT_01]Odufalu FD MS OUTPUT.pdf\\tables\\img\\page_4_table_1.png'
