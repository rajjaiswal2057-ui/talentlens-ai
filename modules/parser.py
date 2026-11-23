"""
TalentLens AI - Resume Parser
Extracts raw text from PDF and DOCX resume files.
"""

from pathlib import Path
import pymupdf as fitz  # PyMuPDF (new import name; keeping alias so rest of file stays unchanged)
import docx  # python-docx


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class ParsingError(Exception):
    """Raised when a resume file can't be read or parsed."""
    pass


def is_allowed_file(filename: str) -> bool:
    """Check whether a filename has a supported resume extension."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def parse_pdf(file_path: str) -> str:
    """Extract raw text from a PDF file using PyMuPDF."""
    text_parts = []
    try:
        with fitz.open(file_path) as pdf:
            if pdf.page_count == 0:
                raise ParsingError("PDF has no pages.")
            for page in pdf:
                text_parts.append(page.get_text())
    except fitz.FileDataError as e:
        raise ParsingError(f"Corrupt or unreadable PDF: {e}")
    except Exception as e:
        raise ParsingError(f"Failed to parse PDF: {e}")

    text = "\n".join(text_parts).strip()
    if not text:
        raise ParsingError(
            "No extractable text found in PDF. It may be a scanned image "
            "without OCR — please upload a text-based PDF."
        )
    return text


def parse_docx(file_path: str) -> str:
    """Extract raw text from a DOCX file using python-docx."""
    try:
        document = docx.Document(file_path)
    except Exception as e:
        raise ParsingError(f"Corrupt or unreadable DOCX: {e}")

    text_parts = [para.text for para in document.paragraphs if para.text.strip()]

    # Resumes often use tables for layout (e.g. skills grids, contact info).
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text_parts.append(cell.text.strip())

    text = "\n".join(text_parts).strip()
    if not text:
        raise ParsingError("No extractable text found in DOCX file.")
    return text


def parse_resume(file_path: str) -> str:
    """
    Parse a resume file (PDF or DOCX) and return its raw text.

    Raises:
        ParsingError: if the file type is unsupported, missing, or unreadable.
    """
    path = Path(file_path)

    if not path.exists():
        raise ParsingError(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(str(path))
    elif suffix == ".docx":
        return parse_docx(str(path))
    else:
        raise ParsingError(
            f"Unsupported file type '{suffix}'. Only PDF and DOCX are supported."
        )