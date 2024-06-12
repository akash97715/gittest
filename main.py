[11:38 PM] Deep, Akash (External)
import os
import uuid
from collections import defaultdict
import pandas as pd
import boto3
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.custom_loguru import logger
from typing import Optional, List
import json
from langchain_community.document_loaders import (
   
    UnstructuredFileLoader,
 
)
from langchain_core.documents import Document
 
class ChunkingException(Exception):
    pass
 
class FileLoaderException(Exception):
    pass
 
class S3UploadError(Exception):
    pass
PARENT_CHUNKS_BUCKET_NAME = os.environ.get("PARENT_CHUNKS_BUCKET_NAME", "")
OCR_BUCKET_NAME = os.environ.get("OCR_BUCKET_NAME", "")
TEXTRACT_ENABLED = json.loads(os.getenv("TEXTRACT_ENABLED", "false").lower())
UNSTRUCTURED_EXCEL_LOADER_ENABLED = json.loads(
    os.getenv("UNSTRUCTURED_EXCEL_LOADER_ENABLED", "false").lower()
)
DOCS_BUCKET_NAME = os.environ.get("DOCS_BUCKET_NAME", "")
 
class ChunkProcessor:
    def __init__(self, filename: str, chunk_size: int, chunk_overlap: int, separators: List[str],
                 cust_metadata: dict, client_id: Optional[str], index_name: Optional[str],
                 parent_doc_id_key: str, extract_images_tables: Optional[bool], chunked_as_parent_child: Optional[bool],
                 custom_metadata: dict, table_confidence_score: Optional[int], custom_extraction_document_path: Optional[str],
                 embed_raw_table: Optional[bool], parent_document_chunk_size: Optional[int], parent_document_chunk_overlap: Optional[int],
                 advance_table_filter_flag: Optional[bool], custom_textract_loader: bool, file_type: str,
                 is_unstructured_loader_enabled: bool, splitter_type: str):
        self.filename = filename
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators
        self.cust_metadata = cust_metadata
        self.client_id = client_id
        self.index_name = index_name
        self.parent_doc_id_key = parent_doc_id_key
        self.extract_images_tables = extract_images_tables
        self.chunked_as_parent_child = chunked_as_parent_child
        self.custom_metadata = custom_metadata
        self.table_confidence_score = table_confidence_score
        self.custom_extraction_document_path = custom_extraction_document_path
        self.embed_raw_table = embed_raw_table
        self.parent_document_chunk_size = parent_document_chunk_size
        self.parent_document_chunk_overlap = parent_document_chunk_overlap
        self.advance_table_filter_flag = advance_table_filter_flag
        self.custom_textract_loader = custom_textract_loader
        self.file_type = file_type
        self.is_unstructured_loader_enabled = is_unstructured_loader_enabled
        self.splitter_type = splitter_type
 
    def _updating_metadata_for_word(self, doc_list: list):
        final_list = []
        for index_number, item in enumerate(doc_list):
            item["page"] = index_number
            final_list.append(item)
        return final_list
 
    def _get_page_metadata(self, metadata, keys_to_exclude_for_ppt, batch=0):
        updated_metadata = []
        for index, item in enumerate(metadata):
            custom_metadata = {}
            for key, value in item.items():
                if key in keys_to_exclude_for_ppt:
                    pass
                else:
                    if key == "page" and self.file_type in [".pdf"] and not TEXTRACT_ENABLED:
                        custom_metadata[key] = value + 1
                    elif key == "page" and self.file_type in [".docx"]:
                        custom_metadata[key] = value + 1
                    elif key == "page_number" and self.file_type in [".pptx", ".ppt"]:
                        custom_metadata["page"] = value
                    else:
                        custom_metadata[key] = value
            custom_metadata = {
                **dict(self.cust_metadata.items()),
                **dict(custom_metadata.items()),
                "batch": batch,
                "chunk_no": index,
            }
            updated_metadata.append(custom_metadata)
        return updated_metadata
 
    def _table_title_merge(self, pages):
        i = 1
        while i < len(pages):
            current_page = pages[i]
            previous_page = pages[i - 1]
            current_page_number = current_page.metadata.get("page_number")
            previous_page_number = previous_page.metadata.get("page_number")
            if (
                current_page.metadata.get("category") == "Table"
                and previous_page.metadata.get("category") == "Title"
                and current_page_number == previous_page_number
            ):
                current_page.page_content = (
                    f"{previous_page.page_content} {current_page.page_content}"
                )
                current_page.metadata.pop("text_as_html", None)
                pages.pop(i - 1)
                i = max(0, i - 1)
            else:
                i += 1
        return pages
 
    def _get_table_text_elements(self, pages):
        table_elements = []
        text_elements = []
        for page in pages:
            if page.metadata["category"] == "Table":
                table_elements.append(page)
            else:
                text_elements.append(page)
        return table_elements, text_elements
 
    def _process_and_refine_text_elements(self, text_elements):
        temptext = ""
        delete_indices = set([])
        for i in range(1, len(text_elements)):
            prev_page = text_elements[i - 1]
            current_page = text_elements[i]
            if current_page.metadata.get("page_number") == prev_page.metadata.get(
                "page_number"
            ):
                if current_page.metadata.get("category") == "NarrativeText":
                    if prev_page.metadata.get("category") == "NarrativeText":
                        continue
                    else:
                        delete_indices.add(i - 1)
                        if temptext != "":
                            current_page.page_content = (
                                temptext + " " + current_page.page_content
                            )
                        else:
                            current_page.page_content = (
                                prev_page.page_content + " " + current_page.page_content
                            )
                        temptext = ""
                else:
                    delete_indices.add(i)
                    if prev_page.metadata.get("category") == "NarrativeText":
                        temptext += (
                            prev_page.page_content + " " + current_page.page_content
                        )
                        delete_indices.add(i - 1)
                    else:
                        temptext += " " + current_page.page_content
            else:
                if temptext != "":
                    prev_page.metadata["category"] = "NarrativeText"
                    prev_page.page_content = temptext
                    temptext = ""
                    delete_indices.remove(i - 1)
        delete_indices = list(delete_indices)
        delete_indices.sort(reverse=True)
        for index in delete_indices:
            del text_elements[index]
        return text_elements
 
    def _process_unstructured_metadata(self, text_elements, table_elements):
        desired_keys = ["source", "page_number", "category"]
        for element in text_elements:
            element.metadata = {
                key: element.metadata[key]
                for key in desired_keys
                if key in element.metadata
            }
        for element in table_elements:
            element.metadata = {
                key: element.metadata[key]
                for key in desired_keys
                if key in element.metadata
            }
        for page in text_elements:
            page.metadata["page"] = page.metadata.pop("page_number")
        for page in table_elements:
            page.metadata["page"] = page.metadata.pop("page_number")
        return text_elements, table_elements
 
    def _get_documents_from_unstructured_loader(self):
        loader = UnstructuredFileLoader(
            self.filename, mode="elements", strategy="hi_res"
        )
        pages = loader.load()
        pages = self._table_title_merge(pages)
        table_elements, text_elements = self._get_table_text_elements(pages)
        text_elements = self._process_and_refine_text_elements(text_elements)
        text_elements, table_elements = self._process_unstructured_metadata(
            text_elements, table_elements
        )
        parent_documents, documents = self._get_documents_chunk(text_elements)
        documents.extend(table_elements)
        return parent_documents, documents
 
    def _get_documents_chunk(self, pages):
        try:
            if self.splitter_type == "RCT":
                text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    separators=self.separators,
                )
            elif self.splitter_type == "CTS":
                # Placeholder for CharacterTextSplitter implementation
                text_splitter = None # Replace with actual CTS implementation
 
            if self.chunked_as_parent_child:
                parent_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                    chunk_size=self.parent_document_chunk_size,
                    chunk_overlap=self.parent_document_chunk_overlap,
                )
                parent_documents = parent_splitter.split_documents(pages)
                docs = []
                full_docs = []
                for doc in parent_documents:
                    _id = "{}/{}/{}".format(self.client_id, self.index_name, uuid.uuid4())
                    sub_docs = text_splitter.split_documents([doc])
                    for _doc in sub_docs:
                        _doc.metadata[self.parent_doc_id_key] = _id
                    docs.extend(sub_docs)
                    full_docs.append((_id, doc))
                return full_docs, docs
            return [], text_splitter.split_documents(pages)
        except Exception as e:
            logger.error(str(e))
            raise ChunkingException(f"Error while creating the chunks: {str(e)}")
[11:38 PM] Deep, Akash (External)
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
 
 
class ChunkingException(Exception):
    pass
 
class FileLoaderException(Exception):
    pass
 
class S3UploadError(Exception):
    pass
 
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
[11:39 PM] Deep, Akash (External)
import json
from fastapi import HTTPException
import httpx
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from app.utils.custom_loguru import logger
from ingest_pipeline.parque_helper import ParquetHelper
from ingest_pipeline.external_api_logic import ias_openai_embeddings  # Assuming this is where the function is
import requests
 
AWS_OPENSEARCH_USERNAME="voxopensearch"
AWS_OPENSEARCH_PASSWORD='''kfxwh9Y4p?y\ST)aH(36%H\i74;Ml'z$G,Po=:!c!e%IOdq,LPan?h+pa|y1,vjY|lesUv=AOYU}hu8<TtGdLzI0%"D1JE16d+)>?)M@,3~6A[:j+qX%ONunqM|VbxzT'''
AWS_OPENSEARCH_HOST="https://vpc-sbx-poc-vsl-docinsight-vox-xrn42vjuqt2kgp6dbqrerkafge.us-east-1.es.amazonaws.com"
IAS_OPENAI_URL="https://mule4api-comm-amer-dev.pfizer.com/vessel-openai-api-v1/completion"
IAS_OPENAI_CHAT_URL="https://mule4api-comm-amer-dev.pfizer.com/vessel-openai-api-v1/chatCompletion"
PINGFEDERATE_URL="https://devfederate.pfizer.com/as/token.oauth2?grant_type=client_credentials"
CLIENT_ID= "6f90ab7409494cdfb67e09de2de63334"
CLIENT_SECRET= "c1c19d8e8B264cA394a7f88a84eF5047"
IAS_EMBEDDINGS_URL="https://mule4api-comm-amer-dev.pfizer.com/vessel-openai-api-v1/embeddings"
IAS_BEDROCK_URL="https://mule4api-comm-amer-dev.pfizer.com/vessel-bedrock-api-v1/completion"
llm_embedding = "text-embedding-ada-002"
llm_model = 'gpt-4-32k'
OCR_BUCKET_NAME="sbx-docinsight-ocr"
TEXTRACT_ENABLED=True
 
def federate_auth() -> str:
    """Obtains auth access token for accessing GPT endpoints"""
    try:
        payload = f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(PINGFEDERATE_URL, headers=headers, data=payload)
        if response.status_code != 200:
            logger.error(
                f"Error calling OpenAI access token API: {response.status_code}, {response.json()}"
            )
            raise Exception(
                f"Error calling OpenAI access token API: {response.status_code}, {response.json()}"
            )
 
        token = response.json()["access_token"]
        return token
    except httpx.TimeoutException as e:
        logger.error(f"Federate Auth Timeout {e}")
        raise HTTPException(status_code=408, detail=f"Error: Federate Auth Timeout")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise e
 
class EmbeddingLoader:
    def __init__(self, parquet_path, engine, client_id, x_vsl_client_id=None, bearer_token=federate_auth(), max_retries=3):
        self.parquet_path = parquet_path
        self.engine = engine
        self.client_id = client_id
        self.x_vsl_client_id = x_vsl_client_id
        self.bearer_token = bearer_token
        self.max_retries = max_retries
        self.df = ParquetHelper.load_parquet(parquet_path)
 
    def process_row(self, texts):
        for attempt in range(self.max_retries):
            try:
                embeddings = ias_openai_embeddings(token=self.bearer_token, raw_text=texts, engine=self.engine)
                return embeddings, None
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed with error: {str(e)}")
                if attempt == self.max_retries - 1:
                    return None, str(e)
        return None, "Maximum retries exceeded"
 
    def update_dataframe(self, idx, embeddings_list, error_message=None):
        if error_message:
            self.df.at[idx, 'embedding'] = error_message
            self.df.at[idx, 'status'] = 'failed'
        else:
            self.df.at[idx, 'embedding'] = json.dumps(embeddings_list)
            self.df.at[idx, 'status'] = 'success'
 
    def process_parquet(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for idx in self.df.index:
                texts = self.df.at[idx, 'chunk']
                futures.append((idx, executor.submit(self.process_row, texts)))
            for idx, future in futures:
                try:
                    embeddings, error_message = future.result()
                    if embeddings is None:
                        self.update_dataframe(idx, None, error_message)
                    else:
                        self.update_dataframe(idx, embeddings)
                except Exception as e:
                    logger.error(f"Error in future for index {idx}: {str(e)}")
        ParquetHelper.save_parquet(self.df, self.parquet_path)
        print(f"Updated Parquet file saved at {self.parquet_path}")
[11:39 PM] Deep, Akash (External)
import os
import pandas as pd
import requests
import json
from typing import List
import logging
#from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
# Placeholder for your constants and exceptions
#IAS_EMBEDDINGS_URL = "https://api.example.com/embeddings"
 
class GenericException(Exception):
    pass
 
 
AWS_OPENSEARCH_USERNAME="voxopensearch"
AWS_OPENSEARCH_PASSWORD='''kfxwh9Y4p?y\ST)aH(36%H\i74;Ml'z$G,Po=:!c!e%IOdq,LPan?h+pa|y1,vjY|lesUv=AOYU}hu8<TtGdLzI0%"D1JE16d+)>?)M@,3~6A[:j+qX%ONunqM|VbxzT'''
AWS_OPENSEARCH_HOST="https://vpc-sbx-poc-vsl-docinsight-vox-xrn42vjuqt2kgp6dbqrerkafge.us-east-1.es.amazonaws.com"
IAS_OPENAI_URL="https://mule4api-comm-amer-dev.pfizer.com/vessel-openai-api-v1/completion"
IAS_OPENAI_CHAT_URL="https://mule4api-comm-amer-dev.pfizer.com/vessel-openai-api-v1/chatCompletion"
PINGFEDERATE_URL="https://devfederate.pfizer.com/as/token.oauth2?grant_type=client_credentials"
CLIENT_ID= "6f90ab7409494cdfb67e09de2de63334"
CLIENT_SECRET= "c1c19d8e8B264cA394a7f88a84eF5047"
IAS_EMBEDDINGS_URL="https://mule4api-comm-amer-dev.pfizer.com/vessel-openai-api-v1/embeddings"
IAS_BEDROCK_URL="https://mule4api-comm-amer-dev.pfizer.com/vessel-bedrock-api-v1/completion"
llm_embedding = "text-embedding-ada-002"
llm_model = 'gpt-4-32k'
OCR_BUCKET_NAME="sbx-docinsight-ocr"
TEXTRACT_ENABLED=True
 
 
def ias_openai_embeddings(token: str, raw_text: List[str], engine: str):
    try:
        url = IAS_EMBEDDINGS_URL
 
        # Ensure raw_text is a list of strings or lists of strings
        if isinstance(raw_text, np.ndarray):
            raw_text = raw_text.tolist()
        elif isinstance(raw_text, list):
            raw_text = [item.tolist() if isinstance(item, np.ndarray) else item for item in raw_text]
 
        payload = {"input": raw_text, "engine": engine}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        logger.info("Triggering embedding endpoint with payload and headers", {"payload": payload, "headers": headers})
        response = requests.post(url, headers=headers, json=payload)
 
        if response.status_code != 200:
            logger.error(
                f"Error calling OpenAI embedding API: {response.status_code}, {response.json()}"
            )
            raise Exception(
                f"Error calling OpenAI embedding API: {response.status_code}, {response.json()}"
            )
        embeddings_temp = json.loads(response.json()["result"])
 
        embeddings = [data['embedding'] for data in embeddings_temp]
        logger.info("Received response from embedding endpoint")
 
        return embeddings
    except Exception as e:
        logger.error("Got the Exception: %s", str(e))
        raise GenericException(e)
[11:40 PM] Deep, Akash (External)
import pandas as pd
import boto3
import uuid
from typing import List
 
class ParquetHelper:
    def __init__(self, chunks: List[str] = None, metadata: List[str] = None, s3_bucket: str = None, s3_prefix: str = None):
        self.chunks = chunks
        self.metadata = metadata
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
 
    def create_parquet(self) -> str:
        # Create a DataFrame with the initial data
        data = {
            'chunk': self.chunks,
            'metadata': self.metadata,
            'embedding': [None] * len(self.chunks),
            'status': [''] * len(self.chunks)
        }
        df = pd.DataFrame(data)
 
        # Generate a unique filename
        parquet_filename = f"{uuid.uuid4()}.parquet"
        local_parquet_path = f"ingest_pipeline/{parquet_filename}"
 
        # Save the DataFrame to a Parquet file locally
        df.to_parquet(local_parquet_path, index=False)
        print(f"Parquet file created locally at {local_parquet_path}")
 
        # Upload the Parquet file to S3
        s3_client = boto3.client("s3")
        s3_key = f"{self.s3_prefix}/{parquet_filename}"
        s3_client.upload_file(local_parquet_path, self.s3_bucket, s3_key)
        print(f"Parquet file uploaded to s3://{self.s3_bucket}/{s3_key}")
 
        # Return the S3 URI
        s3_uri = f"s3://{self.s3_bucket}/{s3_key}"
        return s3_uri
 
    @staticmethod
    def load_parquet(s3_uri: str) -> pd.DataFrame:
        # Parse the S3 URI
        s3_path = s3_uri.replace("s3://", "")
        bucket, key = s3_path.split('/', 1)
 
        # Download the Parquet file from S3
        s3_client = boto3.client('s3')
        local_parquet_path = f"ingest_pipeline/{key.split('/')[-1]}"
        s3_client.download_file(bucket, key, local_parquet_path)
        print(f"Parquet file downloaded locally at {local_parquet_path}")
 
        # Load the Parquet file into a DataFrame
        df = pd.read_parquet(local_parquet_path)
        return df
 
    @staticmethod
    def save_parquet(df: pd.DataFrame, parquet_path: str):
        df.to_parquet(parquet_path, index=False)
        print(f"Parquet file saved at {parquet_path}")
