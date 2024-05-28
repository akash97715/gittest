import os
import json
import boto3
import xml.etree.ElementTree as ET
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import (
    UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    PyPDFLoader,
    AmazonTextractPDFLoader,
    text
)
from app.langchain.custom_textractor import CustomTextractor
from app.utils.custom_loguru import logger
from typing import Optional

OCR_BUCKET_NAME = os.environ.get("OCR_BUCKET_NAME", "")
TEXTRACT_ENABLED = json.loads(os.getenv("TEXTRACT_ENABLED", "false").lower())

class DocumentLoader:
    def __init__(self, filename: str, file_type: str, chunk_processor):
        self.filename = filename
        self.file_type = file_type
        self.chunk_processor = chunk_processor
        self.custom_textract_loader = False

    def _generate_s3_uri_pdf(self):
        try:
            s3_client = boto3.client("s3")
            object_key = self.filename
            with open(object_key, "rb") as file:
                s3_client.upload_fileobj(file, OCR_BUCKET_NAME, object_key)
            s3_uri = f"s3://{OCR_BUCKET_NAME}/{object_key}"
        except Exception as e:
            logger.error(str(e))
            raise S3UploadError(f"Errored while Uploading Document to S3: {str(e)}")
        return s3_uri

    def _get_text(self, element):
        if element.text:
            return element.text.strip()

    def _get_attrs(self, element):
        attrs = element.attrib
        attr_pairs = []
        for attr_name, attr_value in attrs.items():
            attr_pairs.append((attr_name, attr_value))
        return attr_pairs

    def _process_element(self, element):
        result = {
            "tag": element.tag,
            "text": self._get_text(element),
            "attributes": self._get_attrs(element),
            "children": [],
        }
        for child in element:
            result["children"].append(self._process_element(child))
        return result

    def _format_result(self, result, indent=0):
        res_str = " " * indent + result["tag"]
        for attr_name, attr_value in result["attributes"]:
            res_str += " " * (indent + 1) + attr_name + ": " + attr_value
        if result["text"]:
            res_str += " " * (indent + 1) + result["text"] + '\n'
        for child in result["children"]:
            res_str += self._format_result(child, indent + 1)
        return res_str
    
    def _GenericXMLLoader(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        results = []
        for element in root.iter():
            results.append(self._process_element(element))
        output_string = ""
        for result in results:
            output_string += self._format_result(result) + "\n"
        parsed_xml_file_path_output_txt = os.getcwd() + r"\\" + str(filename).replace(".","_") + ".txt"
        with open(parsed_xml_file_path_output_txt, "w", encoding="utf-8") as file:
            file.write(output_string)
        loader = text.TextLoader(parsed_xml_file_path_output_txt, encoding="utf-8")
        return loader, parsed_xml_file_path_output_txt

    async def _get_documents(self):
        try:
            file_temp = ""
            if (
                self.file_type.lower() in [".jpg", ".png", ".pdf", ".jpeg"]
                and TEXTRACT_ENABLED
                and not self.chunk_processor.extract_images_tables
            ):
                textract_client = boto3.client("textract", region_name="us-east-1")
                s3_uri = self._generate_s3_uri_pdf()
                loader = AmazonTextractPDFLoader(
                    s3_uri,
                    client=textract_client,
                    textract_features=["TABLES", "LAYOUT"],
                )
            elif self.file_type == ".pdf" and not TEXTRACT_ENABLED:
                loader = PyPDFLoader(self.filename)
            elif self.file_type == ".docx":
                loader = UnstructuredWordDocumentLoader(self.filename)
            elif self.file_type == ".pptx":
                loader = UnstructuredPowerPointLoader(self.filename, mode="single")
            elif self.file_type == ".xml":
                loader, file_temp = self._GenericXMLLoader(self.filename)
            elif TEXTRACT_ENABLED and self.chunk_processor.extract_images_tables and self.file_type == ".pdf":
                self.custom_textract_loader = True
                s3_uri = self._generate_s3_uri_pdf()
                s3_upload_path = s3_uri + "/textract_ocr/"
                loader = CustomTextractor(
                    file_source=s3_uri,
                    custom_extraction_document_path=self.chunk_processor.custom_extraction_document_path,
                    s3_upload_path=s3_upload_path,
                    filename=self.filename,
                    table_confidence_score=self.chunk_processor.table_confidence_score,
                    additional_metadata=self.chunk_processor.cust_metadata,
                    client_id=self.chunk_processor.client_id,
                    index_name=self.chunk_processor.index_name,
                    advance_table_filter=self.chunk_processor.advance_table_filter_flag,
                    embed_raw_table=self.chunk_processor.embed_raw_table
                )
            else:
                raise FileLoaderException("Unsupported file format")

            if self.custom_textract_loader:
                extracted_data = await loader.load()
                self.chunk_processor.custom_metadata = extracted_data["metadata"]
                parent_documents, documents = self.chunk_processor._get_documents_chunk(extracted_data["raw_texts"])
                combined_table_image_text_docs = (
                    extracted_data["image_summaries"] + extracted_data["table_summaries"] + documents + extracted_data["extra_image_summaries"]
                )
                return parent_documents, combined_table_image_text_docs
            else:
                pages = loader.load()
                parent_documents, documents = self.chunk_processor._get_documents_chunk(pages)
                return parent_documents, documents

        except Exception as e:
            logger.error(str(e))
            raise FileLoaderException(f"Errored while loading the document: {str(e)}")
        finally:
            if file_temp and os.path.exists(file_temp):
                os.remove(file_temp)
