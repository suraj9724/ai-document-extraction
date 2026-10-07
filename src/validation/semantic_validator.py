from extraction.schema import Invoice


class SemanticValidator:

    def validate(self, invoice: Invoice) -> list[str]:
        """
        Validate whether extracted fields make semantic sense.

        This is different from mathematical validation.

        Example:
            state = "India"

        The value is a perfectly valid string,
        but "India" is a country, not a state.
        """

        errors = []

        # Validate seller address
        if invoice.seller:

            if invoice.seller.state:
                if self._looks_like_country(
                    invoice.seller.state
                ):
                    errors.append(
                        "Seller state appears to contain "
                        "a country instead of a state."
                    )

            if invoice.seller.city:
                if self._looks_like_country(
                    invoice.seller.city
                ):
                    errors.append(
                        "Seller city appears to contain "
                        "a country instead of a city."
                    )

        # Validate customer address
        if invoice.customer:

            if invoice.customer.state:
                if self._looks_like_country(
                    invoice.customer.state
                ):
                    errors.append(
                        "Customer state appears to contain "
                        "a country instead of a state."
                    )

            if invoice.customer.city:
                if self._looks_like_country(
                    invoice.customer.city
                ):
                    errors.append(
                        "Customer city appears to contain "
                        "a country instead of a city."
                    )

        return errors

    @staticmethod
    def _looks_like_country(value: str) -> bool:
        """
        Check whether a value looks like a country.

        This is intentionally simple for our learning project.
        A production system could use a proper country/state
        dataset or a dedicated address parser.
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