import os
import json
import asyncio
import uuid
from typing import Optional, List
from collections import defaultdict
import pandas as pd
import boto3
import pathlib
from app.utils.custom_loguru import logger
from app.langchain.s3_doc_store import S3DocStore
from app.chunk_processor import ChunkProcessor
from app.document_loader import DocumentLoader
from langchain_core.documents import Document

PARENT_CHUNKS_BUCKET_NAME = os.environ.get("PARENT_CHUNKS_BUCKET_NAME", "")
TEXTRACT_ENABLED = json.loads(os.getenv("TEXTRACT_ENABLED", "false").lower())
UNSTRUCTURED_EXCEL_LOADER_ENABLED = json.loads(
    os.getenv("UNSTRUCTURED_EXCEL_LOADER_ENABLED", "false").lower()
)
DOCS_BUCKET_NAME = os.environ.get("DOCS_BUCKET_NAME", "")
OCR_BUCKET_NAME = os.environ.get("OCR_BUCKET_NAME", "")


class ChunkingException(Exception):
    pass


class FileLoaderException(Exception):
    pass


class S3UploadError(Exception):
    pass


class IngestionPipeline:
    def __init__(self, filename: str, chunk_size: int, chunk_overlap: int, cust_metadata: dict,
                 client_id: Optional[str] = None, index_name: Optional[str] = None, 
                 custom_extraction_document_path: Optional[str] = "",
                 extract_images_tables: Optional[bool] = False, embed_raw_table: Optional[bool] = False,
                 parent_document_chunk_size: Optional[int] = None, parent_document_chunk_overlap: Optional[int] = None,
                 separators: Optional[List[str]] = ["\n\n", "\n", " ", ""],
                 chunked_as_parent_child: Optional[bool] = True, advance_table_filter_flag: Optional[bool] = False,
                 table_confidence_score: Optional[int] = 20):
        self.filename = filename
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]
        self.cust_metadata = cust_metadata
        self.index_name = index_name
        self.client_id = client_id
        self.parent_doc_id_key = "docinsight_parent_doc_id"
        self.extract_images_tables = extract_images_tables
        self.chunked_as_parent_child = chunked_as_parent_child
        self.custom_metadata = {}
        self.table_confidence_score = table_confidence_score
        self.custom_extraction_document_path = custom_extraction_document_path
        self.embed_raw_table = embed_raw_table
        self.parent_document_chunk_size = parent_document_chunk_size
        self.parent_document_chunk_overlap = parent_document_chunk_overlap
        self.advance_table_filter_flag = advance_table_filter_flag
        self.custom_textract_loader = False
        self.file_type = self._filetype_identification()
        self.is_unstructured_loader_enabled = json.loads(
            os.getenv("UNSTRUCTURED_LOADER_ENABLED", "false").lower()
        )
        self.chunk_processor = ChunkProcessor(
            filename=self.filename,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            cust_metadata=self.cust_metadata,
            client_id=self.client_id,
            index_name=self.index_name,
            parent_doc_id_key=self.parent_doc_id_key,
            extract_images_tables=self.extract_images_tables,
            chunked_as_parent_child=self.chunked_as_parent_child,
            custom_metadata=self.custom_metadata,
            table_confidence_score=self.table_confidence_score,
            custom_extraction_document_path=self.custom_extraction_document_path,
            embed_raw_table=self.embed_raw_table,
            parent_document_chunk_size=self.parent_document_chunk_size,
            parent_document_chunk_overlap=self.parent_document_chunk_overlap,
            advance_table_filter_flag=self.advance_table_filter_flag,
            custom_textract_loader=self.custom_textract_loader,
            file_type=self.file_type,
            is_unstructured_loader_enabled=self.is_unstructured_loader_enabled
        )
        self.document_loader = DocumentLoader(filename=self.filename, file_type=self.file_type)

    def _filetype_identification(self):
        return pathlib.Path(self.filename).suffix

    async def process_files(self):
        try:
            parent_documents, documents = (
                self.chunk_processor._get_documents_from_unstructured_loader()
                if self.is_unstructured_loader_enabled
                else await self.document_loader._get_documents()
            )

            large_file = False
            batch_size = 16
            len_texts = len(documents)
            keys_to_exclude_for_ppt = [
                "file_directory",
                "last_modified",
                "category",
                "filetype",
                "source",
                "text_as_html",
                "page_name",
            ]

            if len_texts <= batch_size:
                page_content = [document.page_content for document in documents]
                page_metadata = [document.metadata for document in documents]

                updated_metadata = (
                    self.chunk_processor._updating_metadata_for_word(page_metadata)
                    if self.file_type == ".docx"
                    else page_metadata
                )

                metadata = self.chunk_processor._get_page_metadata(
                    updated_metadata, keys_to_exclude_for_ppt
                )

            else:
                large_file = True
                page_content_list = [document.page_content for document in documents]
                page_metadata = [document.metadata for document in documents]
                page_content = [
                    page_content_list[i : i + 15]
                    for i in range(0, len(page_content_list), 15)
                ]
                metadata_sublists = [
                    page_metadata[i : i + 15] for i in range(0, len(page_metadata), 15)
                ]
                metadata = [
                    self.chunk_processor._get_page_metadata(sublist, keys_to_exclude_for_ppt, batch=idx)
                    for idx, sublist in enumerate(metadata_sublists)
                ]

            if self.chunked_as_parent_child and len(parent_documents):
                file_store = S3DocStore(PARENT_CHUNKS_BUCKET_NAME)
                updated_parents_documents = [(path, Document(page_content=document.page_content, metadata={**self.cust_metadata, **document.metadata})) for path, document in parent_documents]

                logger.info("Storing parent documents on s3")   
                await file_store.mset(updated_parents_documents)
                logger.info(
                    "For client_id: {client_id} and req_id: {req_id} - Successfully stored parent documents"
                )

        except Exception as e:
            logger.error(e)
            raise ChunkingException(f"Error while chunking the file, {str(e)}")

        return page_content, metadata, large_file
