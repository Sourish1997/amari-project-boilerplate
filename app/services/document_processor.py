from typing import Any

from app.services.llm_service import extract_fields_from_documents
from app.utils.pdf_utils import extract_text_from_pdf
from app.utils.xlsx_utils import extract_data_from_xlsx


def process_documents(file_paths: list[str]) -> dict[str, Any]:
    """
    Process different types of documents and extract relevant information.

    Args:
        file_paths: List of paths to the documents

    Returns:
        dict: Extracted data from documents
    """
    extracted_data = {}

    for file_path in file_paths:
        if file_path.endswith(".xlsx"):
            extracted_data[file_path] = extract_data_from_xlsx(file_path)
        if file_path.endswith(".pdf"):
            extracted_data[file_path] = extract_text_from_pdf(file_path)

    return extracted_data


def process_and_extract_fields(file_paths: list[str]) -> dict[str, Any]:
    """
    Process documents and extract specific shipping/logistics fields using LLM.

    Args:
        file_paths: List of paths to the documents

    Returns:
        dict: Contains both raw document data and extracted structured fields
    """
    # First, process the documents to get raw data
    document_data = process_documents(file_paths)

    # Then, use LLM to extract structured fields
    extracted_fields = extract_fields_from_documents(document_data)

    return {
        "raw_document_data": document_data,
        "extracted_fields": extracted_fields,
        "processed_files": file_paths,
    }
