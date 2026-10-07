from extraction.loader import load_document
from extraction.extractor import InvoiceExtractor

from validation.validator import InvoiceValidator
from validation.completeness import CompletenessChecker
from validation.semantic_validator import SemanticValidator


def main():

    # Path of the invoice that we want to process
    file_path = "data/sample_invoice.pdf"

    # ---------------------------------------------------------
    # STEP 1: Extract raw text from the PDF
    # ---------------------------------------------------------

    document_text = load_document(file_path)

    print("\n========== EXTRACTED TEXT ==========\n")
    print(document_text)

    # ---------------------------------------------------------
    # STEP 2: Extract structured information using the LLM
    # ---------------------------------------------------------

    extractor = InvoiceExtractor()

    invoice = extractor.extract(document_text)

    print("\n========== STRUCTURED DATA ==========\n")
    print(invoice.model_dump_json(indent=2))

    # ---------------------------------------------------------
    # STEP 3: Check whether important fields are missing
    # ---------------------------------------------------------

    completeness_checker = CompletenessChecker()

    missing_fields = completeness_checker.check(invoice)

    print("\n========== COMPLETENESS ==========\n")

    if not missing_fields:

        print("All important fields were extracted.")

    else:

        print("Missing fields:")

        for field in missing_fields:
            print(f"- {field}")

    # ---------------------------------------------------------
    # STEP 4: Validate business rules
    # ---------------------------------------------------------

    validator = InvoiceValidator()

    validation_errors = validator.validate(invoice)

    print("\n========== BUSINESS VALIDATION ==========\n")

    if not validation_errors:

        print("Invoice validation passed.")

    else:

        print("Invoice validation failed.")

        for error in validation_errors:
            print(f"- {error}")


    # ---------------------------------------------------------
    # STEP 5: Validate semantic correctness
    # ---------------------------------------------------------

    semantic_validator = SemanticValidator()

    semantic_errors = semantic_validator.validate(invoice)

    print("\n========== SEMANTIC VALIDATION ==========\n")

    if not semantic_errors:

        print("Semantic validation passed.")

    else:

        print("Semantic validation failed.")

        for error in semantic_errors:
            print(f"- {error}")
        
if __name__ == "__main__":
    main()