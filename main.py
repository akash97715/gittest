from bs4 import BeautifulSoup, NavigableString
from docx import Document
from docx.shared import Pt
from io import BytesIO

class DocumentCreator:
    def __init__(self, payload):
        self.payload = payload

    @staticmethod
    def apply_formatting(run, tag):
        # Apply formatting based on the tag
        if tag in ['strong', 'b']:
            run.bold = True
        if tag in ['em', 'i']:
            run.italic = True
        if tag == 'u':
            run.underline = True

    def add_html_content_to_docx(self, document, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        p = document.add_paragraph()

        for elem in soup.descendants:
            if isinstance(elem, NavigableString):
                print("elem4565456",elem)
                if elem.strip():  # Avoid adding empty strings
                    run = p.add_run(str(elem))
                    self.apply_formatting(run, elem.parent.name)
            elif elem.name in ['p', 'h1', 'h2', 'h3']:
                print("elem2",elem)
                # Add a new paragraph if the tag is p or a heading
                p = document.add_paragraph()
                run = p.add_run(elem.get_text())
                #print(run)
                self.apply_formatting(run, elem.name)
                if elem.name in ['h1', 'h2', 'h3']:
                    run.bold = True
                    p.style = document.styles['Heading ' + elem.name[1]]
                # For a paragraph, apply the default font size
                run.font.size = Pt(12)

    def create_document(self):
        document = Document()
        for placeholder in self.payload['placeholders']:
            html_content = placeholder['content']['text']
            #print("added text",html_content)
            self.add_html_content_to_docx(document, html_content)

            citations = placeholder['content'].get('citations')
            if citations:
                # Add the citations with a smaller font size, as plain text
                citation_text = "Citations:\n" + "\n".join(
                    [f"Source: {c['source']}, Page: {c['page']}" for c in citations]
                )
                p = document.add_paragraph(citation_text)
                for run in p.runs:
                    run.font.size = Pt(8)

        # Instead of saving the file directly, return a BytesIO object
        docx_blob = BytesIO()
        document.save(docx_blob)
        docx_blob.seek(0)
        return docx_blob

# Use the payload provided in the true/false/null form as required by the code
doc_creator = DocumentCreator(payload)
docx_blob = doc_creator.create_document()










{
        "parent_id": null,
        "relative_url": "",
        "name": "smoke-test-doc",
        "content": {},
        "is_template": false,
        "creator_tenant_id": "885ba9df6be84f57b0fcd50b9220a915",
        "is_locked_by": null,
        "created_by": "PRAKAI",
        "created_at": "2024-03-22T15:33:45.379222",
        "id": "264bf5bd-4e62-4726-9387-e14d15b19260",
        "type": "DOC",
        "sequence_no": 1,
        "metadata_info": {},
        "is_deleted": false,
        "is_private": false,
        "modified_by": "PRAKAI",
        "modified_at": "2024-03-23T12:07:46.403093",
        "placeholders": [
            {
                "document_id": "264bf5bd-4e62-4726-9387-e14d15b19260",
                "metadata_info": {
                    "prompt": "Provide a short summary of the study including the purpose, study type and conclusions. Include also the objectives of the study.",
                    "content_index": null,
                    "docs_selected": null
                },
                "sequence_no": 1,
                "is_deleted": false,
                "modified_by": "PRAKAI",
                "modified_at": "2024-03-23T12:07:46.412942",
                "id": "3446251f-8659-484b-a65a-9c9bf49bdf74",
                "content": {
                    "name": "word",
                    "text": "<h1><strong>Title 1</strong></h1><p>static text</p>\nBased on the provided context, it is not possible to determine the purpose of the study, its type, conclusions, and objectives.",
                    "words": "",
                    "citations": [
                        {
                            "page": 1,
                            "source": "INPUTJADETeenpub.pdf",
                            "section": "",
                            "filename": "INPUTJADETeenpub.pdf"
                        },
                        {
                            "page": 1,
                            "source": "INPUTJADETeenpub.pdf",
                            "section": "",
                            "filename": "INPUTJADETeenpub.pdf"
                        },
                        {
                            "page": 1,
                            "source": "INPUTJADETeenpub.pdf",
                            "section": "",
                            "filename": "INPUTJADETeenpub.pdf"
                        },
                        {
                            "page": 1,
                            "source": "INPUTJADETeenpub.pdf",
                            "section": "",
                            "filename": "INPUTJADETeenpub.pdf"
                        },
                        {
                            "page": 1,
                            "source": "INPUTJADETeenpub.pdf",
                            "section": "",
                            "filename": "INPUTJADETeenpub.pdf"
                        }
                    ],
                    "characters": "",
                    "conversation_id": ""
                },
                "created_by": "PRAKAI",
                "created_at": "2024-03-23T12:04:37.557584"
            },
            {
                "document_id": "264bf5bd-4e62-4726-9387-e14d15b19260",
                "metadata_info": {
                    "prompt": "Write a social media post for LinkedIn including following details:\nSummarize the latest breakthrough, the duration of study and Journal names. \nPlease put an emoji in front of the LinkedIn post. \nMention the focus of the study. \nInclude some data for objective, and study design. \n",
                    "content_index": null,
                    "docs_selected": null
                },
                "sequence_no": 2,
                "is_deleted": false,
                "modified_by": "PRAKAI",
                "modified_at": "2024-03-23T12:07:46.412942",
                "id": "d2f1f053-843a-4f5a-97b8-3b5145474eab",
                "content": {
                    "name": "word",
                    "text": "<h1>Title 2</h1><p>static text</p>\nThe social media post for LinkedIn should include details about the study, such as the title, authors, and publication information. It should also mention the key findings of the study, such as the efficacy and safety of abrocitinib plus topical therapy in adolescents with moderate-to-severe atopic dermatitis. Additionally, it may be relevant to mention the funding source and any conflicts of interest disclosed by the authors.",
                    "words": "",
                    "citations": [
                        {
                            "page": 4,
                            "source": "INPUTJADETeenpub.pdf",
                            "section": "",
                            "filename": "INPUTJADETeenpub.pdf"
                        },
                        {
                            "page": 4,
                            "source": "INPUTJADETeenpub.pdf",
                            "section": "",
                            "filename": "INPUTJADETeenpub.pdf"
                        },
                        {
                            "page": 4,
                            "source": "INPUTJADETeenpub.pdf",
                            "section": "",
                            "filename": "INPUTJADETeenpub.pdf"
                        },
                        {
                            "page": 4,
                            "source": "INPUTJADETeenpub.pdf",
                            "section": "",
                            "filename": "INPUTJADETeenpub.pdf"
                        },
                        {
                            "page": 4,
                            "source": "INPUTJADETeenpub.pdf",
                            "section": "",
                            "filename": "INPUTJADETeenpub.pdf"
                        }
                    ],
                    "characters": "",
                    "conversation_id": ""
                },
                "created_by": "PRAKAI",
                "created_at": "2024-03-23T12:04:37.557584"
            }
        ],
        "children": []
    }
