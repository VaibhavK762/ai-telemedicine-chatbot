import pdfplumber
from pathlib import Path
from paddleocr import PaddleOCR
from .config import MIN_PDF_TEXT_LENGTH, OCR_LANGUAGE, SUPPORTED_IMAGE_TYPES
from .logger import logger
from .exceptions import OCRFailure

OCR = PaddleOCR(
    use_angle_cls=True,
    lang=OCR_LANGUAGE
)


def clean_text(text: str) -> str:
    """
    Normalize extracted text.
    """
    return "\n".join(
        line.strip()
        for line in text.splitlines()
        if line.strip()
    )


def extract_pdf_text(file_path: str) -> str:
    """
    Extract text from digital PDFs.
    """
    pages = []
    try:
        logger.info("Attempting digital text extraction from PDF: %s", file_path)
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
    except Exception as e:
        logger.error("Error reading PDF %s: %s", file_path, str(e))
        return ""

    return clean_text("\n".join(pages))


def extract_image_text(file_path: str) -> str:
    """
    Extract text using PaddleOCR.
    """
    try:
        logger.info("Running PaddleOCR on image: %s", file_path)
        result = OCR.ocr(
            file_path,
            cls=True
        )
    except Exception as e:
        logger.error("PaddleOCR failed on image %s: %s", file_path, str(e))
        return ""

    lines = []
    for page in result or []:
        if page is None:
            continue
        for item in page:
            try:
                lines.append(item[1][0])
            except Exception:
                continue

    return clean_text("\n".join(lines))


def extract_scanned_pdf(file_path: str) -> str:
    """
    OCR every page of a scanned PDF.
    Placeholder for future implementation.
    """
    logger.error("Scanned PDF OCR is not yet implemented.")
    raise NotImplementedError("Scanned PDF OCR is not yet implemented.")


def extract_report_text(file_path: str) -> str:
    """
    Extract text from laboratory reports.
    Supports digital PDFs, scanned PDFs, and images.
    """
    extension = Path(file_path).suffix.lower()

    if extension == ".txt":
        logger.info("Reading plain text report: %s", file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return clean_text(f.read())
        except Exception as e:
            raise OCRFailure(f"Failed to read plain text file: {file_path}. Error: {e}")

    if extension == ".pdf":
        text = extract_pdf_text(file_path)
        if len(text) >= MIN_PDF_TEXT_LENGTH:
            logger.info("Successfully extracted %d characters from digital PDF.", len(text))
            return text

        logger.info("Digital PDF text empty or too short (%d chars). Falling back to scanned PDF OCR.", len(text))
        text = extract_scanned_pdf(file_path)
        if not text:
            raise OCRFailure(f"Failed to extract text from PDF: {file_path}")
        return text

    if extension in SUPPORTED_IMAGE_TYPES:
        text = extract_image_text(file_path)
        if not text:
            raise OCRFailure(f"Failed to extract OCR text from image: {file_path}")
        logger.info("Successfully extracted %d characters from image OCR.", len(text))
        return text

    raise ValueError(f"Unsupported file type: {extension}")


if __name__ == "__main__":
    try:
        report = extract_report_text("test_reports/blood_report.pdf")
        print(report)
    except Exception as err:
        print(f"OCR Error: {err}")