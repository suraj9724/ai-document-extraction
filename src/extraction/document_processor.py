from extraction.loader import load_document


class DocumentProcessor:

    def process(self, file_path: str) -> str:
        """
        Load a multi-page document and combine its pages
        into one LLM-ready text representation.

        Page information is preserved in the text so the
        model knows where information came from.
        """

        # Load every page separately.
        pages = load_document(file_path)

        document_parts = []

        for page in pages:

            # Add an explicit page marker before the
            # extracted text.
            page_text = (
                f"[PAGE {page['page_number']}]\n"
                f"{page['text']}"
            )

            document_parts.append(page_text)

        # Join all pages together.
        return "\n\n".join(document_parts)