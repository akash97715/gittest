    def extract_sections_from_toc(self):
        try:
            with zipfile.ZipFile(self.docx_path) as docx:
                xml_content = docx.read('word/document.xml')
            tree = etree.XML(xml_content)
 
            toc_started = False
 
            for elem in tree.iter():
                if 'fldSimple' in elem.tag or 'instrText' in elem.tag:
                    #print(elem.tag)
                    if 'TOC' in ''.join(elem.itertext()):
                        print("===================elem text",elem.itertext())
                        print("===================something",''.join(elem.itertext()))
                        toc_started = True
                        continue
                if toc_started and elem.tag.endswith('}hyperlink'):
                    section_title = ''.join([e for e in elem.itertext()]).strip()
                    if section_title and section_title not in self.sections:
                        self.sections.append(section_title)
                        self.section_contents[section_title] = []
        except Exception as e:
            print(f"Failed in extract_sections_from_toc with error: {e}")
