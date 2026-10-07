from extraction.schema import Invoice


class ExtractionDecision:

    def decide(
        self,
        invoice: Invoice,
        missing_fields: list[str],
        business_errors: list[str],
        semantic_errors: list[str],
    ) -> dict:
        """
        Decide whether the extracted invoice can be
        automatically accepted or should be reviewed.

        This function does NOT perform extraction.

        It only combines the results of all validation
        steps and makes a final decision.
        """

        # ---------------------------------------------------------
        # Combine all problems found during validation
        # ---------------------------------------------------------

        issues = []

        # Missing fields are extraction/completeness issues
        for field in missing_fields:
            issues.append(
                f"Missing field: {field}"
            )

        # Business-rule problems
        issues.extend(business_errors)

        # Semantic problems
        issues.extend(semantic_errors)

        # ---------------------------------------------------------
        # Make the final decision
        # ---------------------------------------------------------

        if issues:

            # Something needs attention, so we should
            # not automatically trust this extraction.
            status = "needs_review"

        else:

            # No problems were detected by our validation
            # layers, so the invoice can be accepted.
            status = "accepted"

        # ---------------------------------------------------------
        # Return a single structured result
        # ---------------------------------------------------------

        return {
            "status": status,
            "invoice": invoice.model_dump(),
            "issues": issues,
        }