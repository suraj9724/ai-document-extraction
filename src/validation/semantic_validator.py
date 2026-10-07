from extraction.schema import Invoice
from validation.review import ReviewField


class SemanticValidator:

    def validate(self, invoice: Invoice) -> list[ReviewField]:
        """
        Check whether extracted values make semantic sense.

        Instead of returning plain error strings, we return
        structured ReviewField objects so we know exactly
        which field needs attention.
        """

        review_fields = []

        # ---------------------------------------------------------
        # Validate seller information
        # ---------------------------------------------------------

        if invoice.seller:

            # Check seller state
            if invoice.seller.state:

                if self._looks_like_country(
                    invoice.seller.state
                ):
                    review_fields.append(
                        ReviewField(
                            field="seller.state",
                            value=invoice.seller.state,
                            reason=(
                                "Value appears to be a country "
                                "rather than a state."
                            ),
                        )
                    )

            # Check seller city
            if invoice.seller.city:

                if self._looks_like_country(
                    invoice.seller.city
                ):
                    review_fields.append(
                        ReviewField(
                            field="seller.city",
                            value=invoice.seller.city,
                            reason=(
                                "Value appears to be a country "
                                "rather than a city."
                            ),
                        )
                    )

        # ---------------------------------------------------------
        # Validate customer information
        # ---------------------------------------------------------

        if invoice.customer:

            # Check customer state
            if invoice.customer.state:

                if self._looks_like_country(
                    invoice.customer.state
                ):
                    review_fields.append(
                        ReviewField(
                            field="customer.state",
                            value=invoice.customer.state,
                            reason=(
                                "Value appears to be a country "
                                "rather than a state."
                            ),
                        )
                    )

            # Check customer city
            if invoice.customer.city:

                if self._looks_like_country(
                    invoice.customer.city
                ):
                    review_fields.append(
                        ReviewField(
                            field="customer.city",
                            value=invoice.customer.city,
                            reason=(
                                "Value appears to be a country "
                                "rather than a city."
                            ),
                        )
                    )

        return review_fields

    @staticmethod
    def _looks_like_country(value: str) -> bool:
        """
        Simple country detection for this learning project.

        In a production application, we would use a proper
        country/address dataset instead of maintaining a small
        hardcoded list.
        """

        countries = {
            "india",
            "australia",
            "united states",
            "usa",
            "canada",
            "united kingdom",
            "uk",
            "germany",
            "france",
            "singapore",
        }

        return value.strip().lower() in countries