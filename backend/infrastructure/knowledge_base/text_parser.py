from domain.knowledge_base.ports import DocumentParserPort

_TEXT_EXTENSIONS = {".txt", ".md", ".rst", ".log", ".csv"}


class TextParser(DocumentParserPort):
    """Parses plain-text files with UTF-8 encoding."""

    async def parse(self, file_bytes: bytes, filename: str) -> str:
        return file_bytes.decode("utf-8", errors="replace")

    def supports(self, filename: str) -> bool:
        return any(filename.lower().endswith(ext) for ext in _TEXT_EXTENSIONS)