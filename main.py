import os
import uuid
from collections import defaultdict
import pandas as pd
import boto3
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.custom_loguru import logger
from typing import Optional, List
from app.ingestion_pipeline import S3UploadError, ChunkingException
from langchain_core.documents import Document

class ChunkProcessor:
    def __init__(self, filename: str, chunk_size: int, chunk_overlap: int, separators: List[str], 
                 cust_metadata: dict, client_id: Optional[str], index_name: Optional[str],
                 parent_doc_id_key: str, extract_images_tables: Optional[bool], chunked_as_parent_child: Optional[bool], 
                 custom_metadata: dict, table_confidence_score: Optional[int], custom_extraction_document_path: Optional[str], 
                 embed_raw_table: Optional[bool], parent_document_chunk_size: Optional[int], parent_document_chunk_overlap: Optional[int], 
                 advance_table_filter_flag: Optional[bool], custom_textract_loader: bool, file_type: str, 
                 is_unstructured_loader_enabled: bool):
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
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=self.separators,
            )
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
