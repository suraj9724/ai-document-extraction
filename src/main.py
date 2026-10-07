from extraction.loader import load_document
from extraction.extractor import InvoiceExtractor


def main():

    file_path = "data/sample_invoice.pdf"

    document_text = load_document(file_path)

    print("\n========== EXTRACTED TEXT ==========\n")
    print(document_text)

    extractor = InvoiceExtractor()

    invoice = extractor.extract(document_text)

    print("\n========== STRUCTURED DATA ==========\n")

    print(invoice.model_dump_json(indent=2))


if __name__ == "__main__":
    main()