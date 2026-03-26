def split_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """
    Splits text into overlapping chunks by character count.

    chunk_size: target characters per chunk
    overlap: characters shared between adjacent chunks to preserve context
    """
    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap

    return chunks
