from extraction.schema import Invoice


class ConfidenceCalculator:

    def calculate(
        self,
        invoice: Invoice,
        missing_fields: list[str],
        semantic_reviews: list,
        business_errors: list[str],
    ) -> dict:
        """
        Calculate a simple field-level confidence score.

        IMPORTANT:
        This is a rule-based score for our learning project.
        It is NOT a true statistical probability.
        """

        confidence = {}

        # ---------------------------------------------------------
        # Invoice number
        # ---------------------------------------------------------

        if invoice.invoice_number:
            confidence["invoice_number"] = self._score(
                field="invoice_number",
                missing_fields=missing_fields,
                semantic_reviews=semantic_reviews,
                business_errors=business_errors,
            )

        # ---------------------------------------------------------
        # Invoice date
        # ---------------------------------------------------------

        if invoice.invoice_date:
            confidence["invoice_date"] = self._score(
                field="invoice_date",
                missing_fields=missing_fields,
                semantic_reviews=semantic_reviews,
                business_errors=business_errors,
            )

        # ---------------------------------------------------------
        # Seller fields
        # ---------------------------------------------------------

        if invoice.seller:

            if invoice.seller.name:
                confidence["seller.name"] = self._score(
                    field="seller.name",
                    missing_fields=missing_fields,
                    semantic_reviews=semantic_reviews,
                    business_errors=business_errors,
                )

            if invoice.seller.city:
                confidence["seller.city"] = self._score(
                    field="seller.city",
                    missing_fields=missing_fields,
                    semantic_reviews=semantic_reviews,
                    business_errors=business_errors,
                )

            if invoice.seller.state:
                confidence["seller.state"] = self._score(
                    field="seller.state",
                    missing_fields=missing_fields,
                    semantic_reviews=semantic_reviews,
                    business_errors=business_errors,
                )

        # ---------------------------------------------------------
        # Customer fields
        # ---------------------------------------------------------

        if invoice.customer:

            if invoice.customer.name:
                confidence["customer.name"] = self._score(
                    field="customer.name",
                    missing_fields=missing_fields,
                    semantic_reviews=semantic_reviews,
                    business_errors=business_errors,
                )

            if invoice.customer.city:
                confidence["customer.city"] = self._score(
                    field="customer.city",
                    missing_fields=missing_fields,
                    semantic_reviews=semantic_reviews,
                    business_errors=business_errors,
                )

            if invoice.customer.state:
                confidence["customer.state"] = self._score(
                    field="customer.state",
                    missing_fields=missing_fields,
                    semantic_reviews=semantic_reviews,
                    business_errors=business_errors,
                )

        # ---------------------------------------------------------
        # Financial fields
        # ---------------------------------------------------------

        for field in [
            "subtotal",
            "gst",
            "total",
        ]:

            value = getattr(invoice, field)

            if value is not None:
                confidence[field] = self._score(
                    field=field,
                    missing_fields=missing_fields,
                    semantic_reviews=semantic_reviews,
                    business_errors=business_errors,
                )

        return confidence

    @staticmethod
    def _score(
        field: str,
        missing_fields: list[str],
        semantic_reviews: list,
        business_errors: list[str],
    ) -> float:
        """
        Start with a high score and reduce it when
        validation finds problems.

        Again, this is only a simple educational scoring
        mechanism.
        """

        score = 1.0

        # A missing field shouldn't normally reach this
        # method, but we handle it safely.
        if field in missing_fields:
            score -= 0.5

        # If semantic validation specifically identified
        # this field, reduce its confidence significantly.
        for review in semantic_reviews:

            if review.field == field:
                score -= 0.5

        # Business validation errors are currently attached
        # to the invoice as a whole, so reduce confidence
        # for financial fields when business validation fails.
        if business_errors and field in {
            "subtotal",
            "gst",
            "total",
        }:
            score -= 0.4

        # Keep the score between 0 and 1.
        return max(0.0, min(1.0, score))