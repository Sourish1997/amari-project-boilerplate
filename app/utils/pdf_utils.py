import logging

import pytesseract
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using OCR.

    Args:
        file_path: Path to the PDF file

    Returns:
        str: Extracted text from the PDF file using OCR

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        PDFInfoNotInstalledError: If poppler is not installed
        Exception: For other PDF processing errors
    """
    try:
        text = ""

        # Convert PDF pages to images
        pages = convert_from_path(file_path)

        # Extract text from each page using OCR
        for i, page in enumerate(pages, 1):
            try:
                # Use pytesseract to extract text from the image
                page_text = pytesseract.image_to_string(page)
                text += page_text + "\n"
                logger.info(f"Successfully processed page {i} of {file_path}")
            except Exception as e:
                logger.warning(
                    f"Failed to extract text from page {i} of {file_path}: {e}"
                )
                continue

        return text.strip()

    except PDFInfoNotInstalledError:
        logger.error("Poppler is not installed")
        raise
    except FileNotFoundError:
        logger.error(f"PDF file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {e}")
        raise
