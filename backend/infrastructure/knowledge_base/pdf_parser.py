import io

from domain.knowledge_base.ports import DocumentParserPort

_PDF_EXTENSIONS = {".pdf"}


class PDFParser(DocumentParserPort):
    """Extracts plain text from PDF files using pymupdf."""

    async def parse(self, file_bytes: bytes, filename: str) -> str:
        import fitz  # pymupdf

        doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
        pages = [page.get_text("text") for page in doc]
        doc.close()
        return "\n".join(pages)

    def supports(self, filename: str) -> bool:
        return any(filename.lower().endswith(ext) for ext in _PDF_EXTENSIONS)