from pathlib import Path
import shutil
import tempfile

from fastapi import FastAPI, File, UploadFile, HTTPException

from extraction.document_processor import DocumentProcessor
from extraction.extractor import InvoiceExtractor
from validation.completeness import CompletenessChecker
from validation.validator import InvoiceValidator
from validation.semantic_validator import SemanticValidator
from validation.confidence import ConfidenceCalculator
from validation.decision import ExtractionDecision


# ---------------------------------------------------------
# Create the FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="AI Document Extraction API",
    version="1.0.0",
)


# ---------------------------------------------------------
# Initialize our AI/validation components once
# ---------------------------------------------------------
#
# We don't want to load the model every time a request
# arrives because loading the model is expensive.
#

document_processor = DocumentProcessor()
extractor = InvoiceExtractor()

completeness_checker = CompletenessChecker()
validator = InvoiceValidator()
semantic_validator = SemanticValidator()
confidence_calculator = ConfidenceCalculator()
decision_engine = ExtractionDecision()


# ---------------------------------------------------------
# Document extraction endpoint
# ---------------------------------------------------------

@app.post("/api/extract")
async def extract_invoice(
    file: UploadFile = File(...)
):
    """
    Accept an uploaded PDF and return structured
    invoice information.
    """

    # -----------------------------------------------------
    # Validate the uploaded file type
    # -----------------------------------------------------

    if file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # -----------------------------------------------------
    # Create a temporary file
    # -----------------------------------------------------
    #
    # UploadFile gives us a file stream.
    # Our existing PDF loader expects a file path,
    # so we temporarily save the uploaded PDF.
    #

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:

            temp_path = Path(temp_file.name)

            # Copy the uploaded file into the temporary file.
            shutil.copyfileobj(
                file.file,
                temp_file,
            )

        # -------------------------------------------------
        # STEP 1: Extract text from the document
        # -------------------------------------------------

        document_text = document_processor.process(
            str(temp_path)
        )

        # -------------------------------------------------
        # STEP 2: Extract structured invoice data
        # -------------------------------------------------

        invoice = extractor.extract(
            document_text
        )

        # -------------------------------------------------
        # STEP 3: Check completeness
        # -------------------------------------------------

        missing_fields = completeness_checker.check(
            invoice
        )

        # -------------------------------------------------
        # STEP 4: Run business validation
        # -------------------------------------------------

        business_errors = validator.validate(
            invoice
        )

        # -------------------------------------------------
        # STEP 5: Run semantic validation
        # -------------------------------------------------

        semantic_reviews = semantic_validator.validate(
            invoice
        )

        # -------------------------------------------------
        # STEP 6: Calculate confidence
        # -------------------------------------------------

        confidence_scores = (
            confidence_calculator.calculate(
                invoice=invoice,
                missing_fields=missing_fields,
                semantic_reviews=semantic_reviews,
                business_errors=business_errors,
            )
        )

        # -------------------------------------------------
        # STEP 7: Make final decision
        # -------------------------------------------------

        decision = decision_engine.decide(
            invoice=invoice,
            missing_fields=missing_fields,
            business_errors=business_errors,
            semantic_reviews=semantic_reviews,
            confidence_scores=confidence_scores,
        )

        # -------------------------------------------------
        # STEP 8: Return final API response
        # -------------------------------------------------

        return {
            "filename": file.filename,
            "status": decision["status"],
            "invoice": decision["invoice"],
            "confidence": confidence_scores,
            "review_fields": decision["review_fields"],
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    finally:

        # -------------------------------------------------
        # Delete the temporary file
        # -------------------------------------------------

        if temp_path and temp_path.exists():

            temp_path.unlink()