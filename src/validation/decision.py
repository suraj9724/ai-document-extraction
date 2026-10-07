from extraction.schema import Invoice
from validation.review import ReviewField


class ExtractionDecision:

    def decide(
        self,
        invoice: Invoice,
        missing_fields: list[str],
        business_errors: list[str],
        semantic_reviews: list[ReviewField],
    ) -> dict:
        """
        Combine all validation results and produce the
        final extraction decision.
        """

        review_fields = []

        # ---------------------------------------------------------
        # 1. Convert missing fields into review items
        # ---------------------------------------------------------

        for field in missing_fields:

            review_fields.append(
                ReviewField(
                    field=field,
                    value=None,
                    reason="Important field was not extracted.",
                )
            )

        # ---------------------------------------------------------
        # 2. Convert business validation errors
        #    into review items
        # ---------------------------------------------------------

        for error in business_errors:

            review_fields.append(
                ReviewField(
                    field="invoice",
                    value=None,
                    reason=error,
                )
            )

        # ---------------------------------------------------------
        # 3. Add semantic validation results
        # ---------------------------------------------------------

        review_fields.extend(
            semantic_reviews
        )

        # ---------------------------------------------------------
        # 4. Decide final status
        # ---------------------------------------------------------

        if review_fields:

            status = "needs_review"

        else:

            status = "accepted"

        # ---------------------------------------------------------
        # 5. Return structured final result
        # ---------------------------------------------------------

        return {
            "status": status,
            "invoice": invoice.model_dump(),
            "review_fields": [
                review.model_dump()
                for review in review_fields
            ],
        }