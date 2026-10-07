from extraction.schema import Invoice


class CompletenessChecker:

    def check(self, invoice: Invoice) -> list[str]:
        """
        Check whether important invoice fields are present.

        This does NOT determine whether the values are correct.
        It only tells us which expected fields are missing.
        """

        missing_fields = []

        # Check invoice number
        if not invoice.invoice_number:
            missing_fields.append("invoice_number")

        # Check invoice date
        if not invoice.invoice_date:
            missing_fields.append("invoice_date")

        # Check seller information
        if invoice.seller is None:
            missing_fields.append("seller")
        elif not invoice.seller.name:
            missing_fields.append("seller.name")

        # Check customer information
        if invoice.customer is None:
            missing_fields.append("customer")
        elif not invoice.customer.name:
            missing_fields.append("customer.name")

        # Check invoice items
        if not invoice.items:
            missing_fields.append("items")

        # Check total
        if invoice.total is None:
            missing_fields.append("total")

        return missing_fields