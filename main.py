    @staticmethod
    def add_hyperlink(paragraph, url, text, tooltip=None):
        part = paragraph.part
        r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)

        hyperlink = OxmlElement('w:hyperlink')
        hyperlink.set(qn('r:id'), r_id)
        if tooltip:
            hyperlink.set(qn('w:tooltip'), tooltip)

        new_run = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')

        # Set the style to 'Hyperlink'
        style = OxmlElement('w:rStyle')
        style.set(qn('w:val'), 'Hyperlink')
        rPr.append(style)

        # Add underline
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rPr.append(u)

        new_run.append(rPr)
        new_run.text = text
        hyperlink.append(new_run)

        paragraph._p.append(hyperlink)

    # The rest of your class definition...
