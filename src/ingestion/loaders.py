"""Load raw documents from various formats."""
from pathlib import Path
from loguru import logger


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        logger.warning("pypdf not installed")
        return ""


def load_docx(path: Path) -> str:
    try:
        from docx import Document as DocxDocument
        doc = DocxDocument(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:
        logger.warning("python-docx not installed")
        return ""


def load_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return load_text(path)
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix == ".docx":
        return load_docx(path)
    logger.warning(f"Unsupported file type: {suffix}")
    return ""