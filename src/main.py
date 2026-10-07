from extraction.loader import load_document
from extraction.extractor import InvoiceExtractor
from extraction.document_processor import DocumentProcessor

from validation.validator import InvoiceValidator
from validation.completeness import CompletenessChecker
from validation.semantic_validator import SemanticValidator
from validation.decision import ExtractionDecision


def main():

    # Path of the invoice that we want to process
    file_path = "data/sample_invoice.pdf"

    # ---------------------------------------------------------
    # STEP 1: Extract raw text from the PDF
    # ---------------------------------------------------------

    # Create the document processor.
    document_processor = DocumentProcessor()

    # Extract all pages and prepare them for the LLM.
    document_text = document_processor.process(file_path)

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

    # Run semantic validation.
    # The result contains structured information about
    # exactly which fields need review.
    semantic_reviews = semantic_validator.validate(invoice)

    print("\n========== SEMANTIC VALIDATION ==========\n")

    if not semantic_reviews:

        print("Semantic validation passed.")

    else:

        print("Semantic validation failed.")

        for error in semantic_reviews:
            print(f"- {error}")
            
    # ---------------------------------------------------------
    # STEP 6: Make the final extraction decision
    # ---------------------------------------------------------

    decision_engine = ExtractionDecision()

    decision = decision_engine.decide(
        invoice=invoice,
        missing_fields=missing_fields,
        business_errors=validation_errors,
        semantic_reviews=semantic_reviews,
    )

    print("\n========== FINAL DECISION ==========\n")

    print(f"Status: {decision['status']}")

    # Get the fields that need human review
    review_fields = decision["review_fields"]

    if review_fields:

        print("\nFields requiring review:")

        for review in review_fields:

            print(
                f"- Field: {review['field']}"
            )

            print(
                f"  Value: {review['value']}"
            )

            print(
                f"  Reason: {review['reason']}"
            )

    else:

        print("No fields require review.")
        
        
    # ---------------------------------------------------------
    # Check for duplicate line items
    # ---------------------------------------------------------

    duplicate_errors = validator.find_duplicate_items(
        invoice
    )

    validation_errors.extend(
        duplicate_errors
    )

if __name__ == "__main__":
    main()