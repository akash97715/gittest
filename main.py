import asyncio
from collections import defaultdict
import os
import json
import boto3
import uuid
from langchain_community.document_loaders.csv_loader import (
    CSVLoader,
)
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredFileLoader,
    PyPDFLoader,
    AmazonTextractPDFLoader,
    text
)
import xml.etree.ElementTree as ET
from app.langchain.custom_textractor import CustomTextractor
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pathlib

from app.utils.custom_loguru import logger
from typing import Optional, List
import pandas as pd
import openpyxl
import xlrd
from xlsxwriter.workbook import Workbook
import pyarrow as pa
import io
import time
from app.langchain.s3_doc_store import S3DocStore

PARENT_CHUNKS_BUCKET_NAME = os.environ.get("PARENT_CHUNKS_BUCKET_NAME", "")
OCR_BUCKET_NAME = os.environ.get("OCR_BUCKET_NAME", "")
TEXTRACT_ENABLED = json.loads(os.getenv("TEXTRACT_ENABLED", "false").lower())
UNSTRUCTURED_EXCEL_LOADER_ENABLED = json.loads(
    os.getenv("UNSTRUCTURED_EXCEL_LOADER_ENABLED", "false").lower()
)
DOCS_BUCKET_NAME = os.environ.get("DOCS_BUCKET_NAME", "")


class ChunkingException(Exception):
    pass


class FileLoaderException(Exception):
    pass


class S3UploadError(Exception):
    pass


class FileProcessor:
    def __init__(
        self,
        filename: str,
        chunk_size: int,
        chunk_overlap: int,
        cust_metadata: dict,
        client_id: Optional[str] = None,
        index_name: Optional[str] = None,
        custom_extraction_document_path: Optional[str] = "",
        extract_images_tables: Optional[bool] = False,
        embed_raw_table: Optional[bool] = False,
        parent_document_chunk_size: Optional[int] = None,
        parent_document_chunk_overlap: Optional[int] = None,
        separators: Optional[List[str]] = ["\n\n", "\n", " ", ""],
        chunked_as_parent_child: Optional[bool] = True,
        advance_table_filter_flag: Optional[bool] = False,
        table_confidence_score: Optional[int] = 20
    ):
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
        self.embed_raw_table=embed_raw_table
        self.parent_document_chunk_size = parent_document_chunk_size
        self.parent_document_chunk_overlap = parent_document_chunk_overlap
        self.advance_table_filter_flag=advance_table_filter_flag
        self.custom_textract_loader = False
        self.file_type = self._filetype_identification()
        self.is_unstructured_loader_enabled = json.loads(
            os.getenv("UNSTRUCTURED_LOADER_ENABLED", "false").lower()
        )

    def _filetype_identification(self):
        return pathlib.Path(self.filename).suffix

    def _updating_metadata_for_word(self, doc_list: list):
        """This function takes list of dict containing metadata as an input"""

        """returns an updated metadata containing page number in it"""
        final_list = []
        for index_number, item in enumerate(doc_list):
            item["page"] = index_number
            final_list.append(item)
        return final_list

    def convert_pandas_to_parquet(self, df, s3_path, sheet_name, s3_client):
        """This function is used to explicitly convert pandas dataframes to parquet format."""

        try:
            with io.BytesIO() as parquet_buffer:
                try:
                    conversion_status = True
                    while conversion_status:
                        try:
                            # Direct conversion to parquet
                            df.to_parquet(parquet_buffer, compression="gzip")
                            parquet_buffer.seek(0)
                            conversion_status = False
                        except pa.ArrowTypeError as e:
                            error_message = str(e)
                            logger.warning(f"ArrowTypeError occurred: {error_message}")
                            expected_type = error_message.split("Expected ")[1].split(
                                ","
                            )[0]
                            actual_type = error_message.split("got a '")[1].split(
                                "' object"
                            )[0]
                            logger.warning(
                                "Expected type:",
                                expected_type,
                                "\nActual type:",
                                actual_type,
                            )
                            problematic_column = error_message.split("column ")[
                                1
                            ].split(" ")[0]
                            logger.warning(
                                f"Attempting to convert column: {problematic_column} which is in {actual_type} type to {expected_type} type."
                            )

                            # Convert the problematic column based on expected type
                            if expected_type == "bytes":
                                df[problematic_column] = (
                                    df[problematic_column]
                                    .astype(str)
                                    .apply(lambda x: x.encode("utf-8"))
                                )
                                logger.info(
                                    "Problematic column converted from bytes to string type."
                                )
                            elif expected_type == "int":
                                df[problematic_column] = df[problematic_column].astype(
                                    int
                                )
                                logger.info("Problematic column converted to int type.")
                            else:
                                df[problematic_column] = df[problematic_column].astype(
                                    str
                                )
                                logger.info(
                                    "Problematic column converted to string type."
                                )
                            conversion_status = True

                        except Exception as e:
                            error_message = str(e)
                            logger.warning(f"General error occurred: {error_message}")
                            problematic_column = error_message.split("column")[1].split(
                                " "
                            )[1]
                            df[problematic_column] = df[problematic_column].astype(str)
                            logger.info("Column converted to string type.")
                            conversion_status = True
                except Exception as e:
                    logger.error(f"Parquet conversion failed: {str(e)}")
                    raise e

                try:
                    s3_uri = self.upload_parquet_file(
                        s3_path, sheet_name, s3_client, parquet_buffer
                    )
                except Exception as e:
                    logger.error(f"Upload of Parquet file failed: {str(e)}")
                    raise e

                return s3_uri
        except Exception as e:
            raise e
        finally:
            parquet_buffer.close()

    def dataframe_processing(self, file_type, s3_path, s3_client) -> list:
        """Function to pre-process daatframes (.xlsx/.csv/.xls) files.
        Upload the pre-processed files to S3 path as parquet files."""

        try:
            s3_uri_list = []
            filename = self.filename
            file_path = filename

            if file_type == ".csv":
                logger.info("The file type is .csv")

                # Reading .csv file using pandas csv
                try:
                    df = pd.read_csv(file_path)
                except Exception as e:
                    raise Exception(
                        "Invalid csv file format. Unable to load. Please check the format"
                    )

                # Converting pandas dataframe to parquet format
                try:
                    # Extracting file name without .csv extention
                    extracted_filename = os.path.splitext(file_path)[0]
                    s3_uri = self.convert_pandas_to_parquet(
                        df, s3_path, extracted_filename, s3_client
                    )
                    s3_uri_list.append(s3_uri)
                except Exception as e:
                    raise e

            else:
                try:
                    if file_type == ".xlsx":
                        logger.info(f"The file type is {file_type}.")

                        # Extracting headers and unmerging excel file cells

                        # Open the Excel file with openpyxl
                        wb = openpyxl.load_workbook(file_path, data_only=True)

                        # Extract the sheet names available in the file
                        sheet_names = wb.sheetnames
                        header_dict = {}
                        for sheet_num in sheet_names:
                            # Detecting headers
                            df = pd.read_excel(
                                file_path, sheet_name=sheet_num, header=None
                            )
                            header_row = 0
                            for i, row in df.iterrows():
                                if row.notnull().all():
                                    header_row = i
                                    break
                                else:
                                    header_row = 0
                            header_dict[sheet_num] = header_row

                            # Load data from a particular sheet
                            ws = wb[sheet_num]

                            # Identiying merged cells in the file
                            merged_cells = list(ws.merged_cells.ranges)

                            # Unmerge cells and re-assign values to unmerged cells
                            for merged_cells_range in merged_cells:
                                # unmerging cells
                                ws.unmerge_cells(str(merged_cells_range))
                                min_row, min_col, max_row, max_col = (
                                    merged_cells_range.min_row,
                                    merged_cells_range.min_col,
                                    merged_cells_range.max_row,
                                    merged_cells_range.max_col,
                                )

                                # Assigning values to unmerged empty cells using the first non-empty cell.
                                for row in range(min_row, max_row + 1):
                                    for col in range(min_col, max_col + 1):
                                        # Access the cell using row and column indices
                                        cell = ws.cell(row=row, column=col)
                                        if cell.value is None:
                                            for prev_cell in range(
                                                cell.column - 1, 0, -1
                                            ):
                                                if (
                                                    ws.cell(
                                                        row=cell.row, column=prev_cell
                                                    ).value
                                                    is not None
                                                ):
                                                    cell.value = ws.cell(
                                                        row=cell.row, column=prev_cell
                                                    ).value
                                                    break
                    else:
                        logger.info(f"The file type is {file_type}.")

                        wb = xlrd.open_workbook(file_path, formatting_info=True)
                        sheet_names = wb.sheet_names()
                        header_dict = {}
                        for sheet_num in sheet_names:
                            # Detecting headers
                            df = pd.read_excel(
                                file_path, sheet_name=sheet_num, header=None
                            )
                            header_row = 0
                            for i, row in df.iterrows():
                                if row.notnull().all():
                                    header_row = i
                                    break
                                else:
                                    header_row = 0
                            header_dict[sheet_num] = header_row

                except Exception as e:
                    logger.error(str(e))
                    raise Exception(
                        "Error while detecting or unmerging .xlsx/.xls files."
                    )

                empty_sheet_count = []
                # Converting to parquet
                for sheet_name, header_val in header_dict.items():
                    sheet_name = sheet_name
                    header_index = header_val
                    logger.info("Sheet Name: ", sheet_name, "\nHeader: ", header_index)

                    # Extracting data from the workbook with the specified sheet and convert to pandas dataframe
                    if file_type == ".xlsx":
                        data = list(wb[sheet_name].values)
                    else:
                        sheet = wb.sheet_by_name(sheet_name)
                        data = [
                            sheet.row_values(row_index)
                            for row_index in range(sheet.nrows)
                        ]

                    # To check if the sheet is empty or not.
                    if len(data) != 0:
                        logger.info("Sheet not empty")
                        try:
                            dfCol_list = data[header_index]

                            # Checking for duplicate column names.
                            nonDup_dfCol_list = []
                            count_dict = {}

                            for item in dfCol_list:
                                item = "_".join(str(item).strip().split(" "))
                                if item in count_dict:
                                    count_dict[item] += 1
                                    new_item = f"{item}_{count_dict[item]}"
                                    nonDup_dfCol_list.append(new_item)
                                else:
                                    nonDup_dfCol_list.append(item)
                                    count_dict[item] = 1

                            df = pd.DataFrame(
                                data[header_index + 1 :], columns=nonDup_dfCol_list
                            )

                            # Changing all object datatype columns to string to avoid parquet conversion errors.
                            for cols in df.columns:
                                if df[cols].dtypes == "object":
                                    df[cols] = df[cols].astype(str)

                            # Adding the files to different folders based on sheets and file names as parquet files in S3
                            s3_uri = self.convert_pandas_to_parquet(
                                df, s3_path, sheet_name, s3_client
                            )
                            s3_uri_list.append(s3_uri)

                        except Exception as e:
                            raise e

                    else:
                        logger.error("Excel sheet empty")
                        empty_sheet_count.append(1)

                if len(empty_sheet_count) == len(header_dict.keys()):
                    raise Exception("Provided excel files are empty")

            return s3_uri_list
        except Exception as e:
            logger.error(f"Error in dataframe_processing: {repr(e)}")
            raise e
        finally:
            # Dispose of the DataFrame
            if "df" in locals():
                del df

    def get_header_row(self, df):
        """This function will return the index of the header row with the smallest number of NA values
        among the first 10 rows. If there are multiple rows with the same smallest number of NA values,
        it will return the first one."""
        header_row = 0
        min_na_count = (
            df.shape[1] + 1
        )  # initialize with a number larger than possible na count
        for i, row in df.iterrows():
            if i >= 10:  # only consider first 10 rows
                break
            if row.notnull().all():
                header_row = i
                break
            na_count = row.isnull().sum()  # count NA values in this row
            if na_count < min_na_count:  # if this row has fewer NA values
                min_na_count = na_count  # update minimum NA count
                header_row = i  # update header row
        return header_row

    def rename_duplicate_columns(self, df):
        counts = defaultdict(int)
        for i in range(len(df.columns)):
            counts[df.columns[i]] += 1
            if counts[df.columns[i]] > 1:
                df.columns.values[i] = (
                    df.columns.values[i] + "_" + str(counts[df.columns[i]] - 1)
                )
        return df

    def process_tabular_file(
        self,
        client_id: str,
        request_id: str,
        file_type: str,
        filename: str,
        final_folder: str,
    ) -> list:
        # initializing boto client
        s3_client = boto3.client("s3", "us-east-1")
        s3_path = client_id + "/" + request_id + "/" + final_folder + "/"

        if (
            file_type == ".xls" or file_type == ".xlsx"
        ) and UNSTRUCTURED_EXCEL_LOADER_ENABLED:
            s3_uri_list = self.process_unstructured_tabular_file(
                file_type, filename, s3_path, s3_client
            )
        else:
            s3_uri_list = self.dataframe_processing(file_type, s3_path, s3_client)
        return s3_uri_list

    def process_unstructured_tabular_file(
        self, file_type: str, filename: str, s3_path: str, s3_client
    ) -> list:
        s3_uri_list = []
        try:
            if file_type == ".xls" or file_type == ".xlsx":
                loader = UnstructuredExcelLoader(
                    filename,
                    mode="elements",
                )
            else:
                raise FileLoaderException("Unsupported file format")

            docs = loader.load()

            for i, doc in enumerate(docs):
                if doc.metadata.get("category", "") == "Table":
                    html_content = doc.metadata.get("text_as_html", "")
                    if html_content == "":
                        continue

                    sheet_name = doc.metadata.get("page_name", "")

                    # Read html table into Pandas Dataframe
                    excel_data = pd.read_html(html_content, header=None)
                    if len(excel_data) <= 0:
                        continue

                    # Get data into dataframe.
                    df = excel_data[0]

                    # Get header row index.
                    header_row_index = self.get_header_row(df)

                    # Set header row
                    df.columns = df.iloc[header_row_index]

                    # After setting the new header, drop the original row that contained the header data
                    df = df.drop(header_row_index)

                    # Set all column names in the DataFrame df to string
                    df.columns = df.columns.astype(str)

                    # Rename duplicate columns
                    df = self.rename_duplicate_columns(df)

                    s3_uri = self.convert_pandas_to_parquet(
                        df, s3_path, f"{sheet_name}.parquet", s3_client
                    )

                    s3_uri_list.append(s3_uri)

            return s3_uri_list
        except Exception as e:
            logger.error(f"Failed to process {filename} file. Error: {repr(e)}")
            raise Exception(f"Failed to load {filename} file. Error: {str(e)}")

    def upload_parquet_file(self, s3_path, file_name, s3_client, parquet_buffer):
        # Writing the parquet files to S3
        try:
            key = s3_path + file_name + ".parquet"
            s3_uri = f"s3://{DOCS_BUCKET_NAME}/{key}"
            s3_client.upload_fileobj(
                Fileobj=parquet_buffer,
                Bucket=DOCS_BUCKET_NAME,
                Key=key,
            )
            logger.info(
                f" {file_name} file successfully uploaded to S3 Processed folder."
            )
            return s3_uri

        except Exception as e:
            logger.error(f"Parquet file upload to S3 error:{repr(e)}")
            raise S3UploadError(
                f"Error while Uploading Document to S3 Processed folder: {str(e)}"
            )

    def upload_docs_to_s3(self, file_name, client_id, request_id, final_folder):
        """Function to upload all types of docs to S3 path through ingestion end point."""

        try:
            s3_client = boto3.client("s3")
            filename = self.filename
            s3_path = client_id + "/" + request_id + "/" + final_folder + "/"
            key = s3_path + filename
            with open(file_name, "rb") as file:
                s3_client.upload_fileobj(file, Bucket=DOCS_BUCKET_NAME, Key=key)
            s3_uri = f"s3://{DOCS_BUCKET_NAME}/{key}"
        except Exception as e:
            logger.error(str(e))
            raise S3UploadError(f"Errored while Uploading Document to S3: {str(e)}")

        return s3_uri

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

    #%% Xml Parsers function starts
    # Extract element text
    def _get_text(self, element):
        if element.text:
            return element.text.strip()


    # Extract attribute name-value pairs
    def _get_attrs(self, element):
        attrs = element.attrib
        attr_pairs = []
        for attr_name, attr_value in attrs.items():
            attr_pairs.append((attr_name, attr_value))
        return attr_pairs


    # Process elements recursively
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

    # Convert the parsed results to a formatted string
    def _format_result(self, result, indent=0,):
        res_str = " " * indent + result["tag"] #+ '\n'
        for attr_name, attr_value in result["attributes"]:
            res_str += " " * (indent + 1) + attr_name + ": " + attr_value #+ '\n'
        if result["text"]:
            res_str += " " * (indent + 1) + result["text"] + '\n'
        for child in result["children"]:
            res_str += self._format_result(child, indent + 1)
        return res_str
    
    def _GenericXMLLoader(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        # Iterate over elements recursively
        results = []
        for element in root.iter():
            results.append(self._process_element(element))

        # Convert the parsed results to a string
        output_string = ""
        for result in results:
            output_string += self._format_result(result) + "\n"

        parsed_xml_file_path_output_txt = os.getcwd() + r"\\" + str(filename).replace(".","_") + ".txt"

        with open(parsed_xml_file_path_output_txt, "w", encoding="utf-8") as file:
                    file.write(output_string)
        loader = text.TextLoader(parsed_xml_file_path_output_txt, encoding="utf-8")
        return loader, parsed_xml_file_path_output_txt
    #%% Xml Parsers function ends

    async def _get_documents(self):
        """This function load the documents in list by taking filename as argument"""
        try:
            # Rel 5.0 - Commented below lines to use agent instead of document loaders.
            # if self.file_type == ".xlsx":
            #     loader = UnstructuredExcelLoader(self.filename, mode="elements")
            # elif self.file_type == ".csv":
            #     loader = CSVLoader(self.filename)
            file_temp = ""
            if (
                self.file_type.lower() in [".jpg", ".png", ".pdf", ".jpeg"]
                and TEXTRACT_ENABLED
                and not self.extract_images_tables
            ):
                textract_client = boto3.client("textract", region_name="us-east-1")
                # TODO Use s3_uri instead
                s3_uri = self._generate_s3_uri_pdf()
                loader = AmazonTextractPDFLoader(
                    s3_uri,
                    client=textract_client,
                    textract_features=["TABLES", "LAYOUT"],
                )
            elif (
                self.file_type == ".pdf"
                and not TEXTRACT_ENABLED
            ):
                # TODO Try s3 file path isntead of local file
                loader = PyPDFLoader(self.filename)
            elif self.file_type == ".docx":
                loader = UnstructuredWordDocumentLoader(self.filename)
            elif self.file_type == ".pptx":
                loader = UnstructuredPowerPointLoader(self.filename, mode="single")
            elif self.file_type == ".xml":
                loader, file_temp  = self._GenericXMLLoader(self.filename)
            elif TEXTRACT_ENABLED and self.extract_images_tables and self.file_type == ".pdf":
                self.custom_textract_loader = True
                s3_uri = self._generate_s3_uri_pdf()
                s3_upload_path = s3_uri + "/textract_ocr/"
                loader = CustomTextractor(
                    file_source=s3_uri,
                    custom_extraction_document_path=self.custom_extraction_document_path,
                    s3_upload_path=s3_upload_path,
                    filename=self.filename,
                    table_confidence_score=self.table_confidence_score,
                    additional_metadata=self.cust_metadata,
                    client_id=self.client_id,
                    index_name=self.index_name,
                    advance_table_filter=self.advance_table_filter_flag,
                    embed_raw_table=self.embed_raw_table
                )

            else:
                raise FileLoaderException("Unsupported file format")

            if self.custom_textract_loader:
                extracted_data = await loader.load()
                
                self.custom_metadata = extracted_data["metadata"]

                parent_documents, documents = self._get_documents_chunk(extracted_data["raw_texts"])
                combined_table_image_text_docs = (
                    extracted_data["image_summaries"] + extracted_data["table_summaries"] + documents + extracted_data["extra_image_summaries"]
                )

                return parent_documents, combined_table_image_text_docs

            else:
                pages = loader.load()
                parent_documents, documents = self._get_documents_chunk(pages)
                return parent_documents, documents

        except Exception as e:
            logger.error(str(e))
            raise FileLoaderException(f"Errored while loading the document: {str(e)}")
        
        finally:
            if file_temp and os.path.exists(file_temp):
                os.remove(file_temp)

    def _table_title_merge(self, pages):
        """This function processes a list of pages, merging the content of pages labeled as 'Table' with the preceding 'Title' pages if they share the same page number."""

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
        """This function segregates pages into two lists, table_elements and text_elements, based on their category ('Table' or other)."""

        table_elements = []
        text_elements = []

        for page in pages:
            if page.metadata["category"] == "Table":
                table_elements.append(page)
            else:
                text_elements.append(page)

        return table_elements, text_elements

    def _process_and_refine_text_elements(self, text_elements):
        """This method processes a list of text elements, identifying consecutive pages with the same page number. If a page is categorized as "NarrativeText," it combines its content with the preceding page's content, excluding redundant occurrences. The method uses a set of indices to track and delete redundant pages while updating their metadata and content accordingly."""

        temptext = ""
        delete_indices = set([])

        for i in range(1, len(text_elements)):
            prev_page = text_elements[i - 1]
            current_page = text_elements[i]

            # condition to check the page_number of the previous and current page
            if current_page.metadata.get("page_number") == prev_page.metadata.get(
                "page_number"
            ):
                if (
                    current_page.metadata.get("category") == "NarrativeText"
                ):  # is a narrativeText
                    if prev_page.metadata.get("category") == "NarrativeText":
                        continue
                    else:  # prev not narrative
                        delete_indices.add(i - 1)

                        # Concatenate page content based on the existence of temptext
                        if temptext != "":
                            current_page.page_content = (
                                temptext + " " + current_page.page_content
                            )
                        else:
                            current_page.page_content = (
                                prev_page.page_content + " " + current_page.page_content
                            )
                        temptext = ""
                else:  # not a NarrativeText
                    delete_indices.add(i)

                    # Concatenate page content of both pages and add the index of the previous page to delete_indices set
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

        # Deleting indices which are not required
        delete_indices = list(delete_indices)
        delete_indices.sort(reverse=True)

        for index in delete_indices:
            del text_elements[index]

        return text_elements

    def _process_unstructured_metadata(self, text_elements, table_elements):
        """This code selectively retains only the desired keys in the metadata of both text_elements and table_elements"""

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

        # Renaming 'page_number' as 'page'
        for page in text_elements:
            page.metadata["page"] = page.metadata.pop("page_number")
        for page in table_elements:
            page.metadata["page"] = page.metadata.pop("page_number")

        return text_elements, table_elements

    def _get_documents_from_unstructured_loader(self):
        """This function load the documents by taking filename as argument and processes them."""

        loader = UnstructuredFileLoader(
            self.filename, mode="elements", strategy="hi_res"
        )
        pages = loader.load()

        # Logic for adding previous Titles to tables if exists
        pages = self._table_title_merge(pages)

        # Logic to separating table and text elements
        table_elements, text_elements = self._get_table_text_elements(pages)

        # Logic for merging among text_elements
        text_elements = self._process_and_refine_text_elements(text_elements)

        # Cleaning metadata
        text_elements, table_elements = self._process_unstructured_metadata(
            text_elements, table_elements
        )

        # Chunking the text_elements
        parent_documents, documents = self._get_documents_chunk(text_elements)

        # Concatenating un-chunked table_elements to chunked text_elements
        documents.extend(table_elements)

        return parent_documents, documents

    def _get_documents_chunk(self, pages):
        "this function returns the chunks and metadata based on chunk size and overlap by taking list of document as argument"
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

    def _get_page_metadata(self, metadata, keys_to_exclude_for_ppt, batch=0):
        """This function returns the updated metadata by stacking the custom metadata received in the request"""
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

    def fetch_custom_metadata(self):
        return self.custom_metadata

    async def process_files(self):
        """This function is the main function which is responsible to process the files and return the page contents and metadata
        with flag that says we need to ingest in loop or directly once"""
        try:
            parent_documents, documents = (
                self._get_documents_from_unstructured_loader()
                if self.is_unstructured_loader_enabled
                else await self._get_documents()
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
                    self._updating_metadata_for_word(page_metadata)
                    if self.file_type == ".docx"
                    else page_metadata
                )

                metadata = self._get_page_metadata(
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
                    self._get_page_metadata(sublist, keys_to_exclude_for_ppt, batch=idx)
                    for idx, sublist in enumerate(metadata_sublists)
                ]

            if self.chunked_as_parent_child and len(parent_documents):
                file_store = S3DocStore(PARENT_CHUNKS_BUCKET_NAME)
                # add custom metadata to parent chunk
                updated_parents_documents = [(path, Document(page_content=document.page_content, metadata={**self.cust_metadata, **document.metadata})) for path, document in parent_documents]

                logger.info("Storing parent documents on s3")   
                # Store parent chunks on S3
                await file_store.mset(updated_parents_documents)
                logger.info(
                    "For client_id: {client_id} and req_id: {req_id} - Successfully stored parent documents"
                )

        except Exception as e:
            logger.error(e)
            raise ChunkingException(f"Error while chunking the file, {str(e)}")

        return page_content, metadata, large_file
