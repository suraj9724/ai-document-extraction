from extraction.schema import Invoice
from validation.review import ReviewField


class ExtractionDecision:

    def decide(
        self,
        invoice: Invoice,
        missing_fields: list[str],
        business_errors: list[ReviewField],
        semantic_reviews: list[ReviewField],
        confidence_scores: dict,
    ) -> dict:

        review_fields = []

        # ---------------------------------------------------------
        # Missing fields
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
        # Business validation errors
        # ---------------------------------------------------------
        #
        # These already contain the exact field, value and page.
        #

        review_fields.extend(business_errors)

        # ---------------------------------------------------------
        # Semantic validation errors
        # ---------------------------------------------------------

        review_fields.extend(semantic_reviews)

        # ---------------------------------------------------------
        # Confidence warnings
        # ---------------------------------------------------------

        for field, score in confidence_scores.items():

            if score < 0.70:

                already_reported = any(
                    review.field == field
                    for review in review_fields
                )

                if not already_reported:
                    review_fields.append(
                        ReviewField(
                            field=field,
                            value=None,
                            reason=(
                                f"Low extraction confidence: "
                                f"{score:.2f}"
                            ),
                        )
                    )

        status = (
            "needs_review"
            if review_fields
            else "accepted"
        )

        return {
            "status": status,
            "invoice": invoice.model_dump(),
            "review_fields": [
                review.model_dump()
                for review in review_fields
            ],
        }