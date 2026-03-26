import io

from domain.knowledge_base.ports import DocumentParserPort

_DOCX_EXTENSIONS = {".docx", ".doc"}


class DOCXParser(DocumentParserPort):
    """Extracts plain text from Word documents using python-docx."""

    async def parse(self, file_bytes: bytes, filename: str) -> str:
        from docx import Document

        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    def supports(self, filename: str) -> bool:
        return any(filename.lower().endswith(ext) for ext in _DOCX_EXTENSIONS)