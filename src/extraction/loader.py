from pathlib import Path
from pypdf import PdfReader


def load_document(file_path: str) -> list[dict]:
    """
    Extract text from every page of a PDF.

    Instead of returning one large string, we keep
    the page number together with its extracted text.

    Example result:

    [
        {
            "page_number": 1,
            "text": "Invoice ..."
        },
        {
            "page_number": 2,
            "text": "Items ..."
        }
    ]
    """

    path = Path(file_path)

    # Make sure the PDF actually exists.
    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    reader = PdfReader(path)

    pages = []

    # Process every page separately.
    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        # Extract text from the current page.
        text = page.extract_text() or ""

        # Ignore completely empty pages.
        if text.strip():

            pages.append({
                "page_number": page_number,
                "text": text.strip(),
            })

    return pages