from extraction.schema import Invoice


class InvoiceValidator:

    def validate(self, invoice: Invoice) -> list[str]:
        """
        Validate the extracted invoice using business rules.

        Returns:
            A list of validation errors.
            An empty list means the invoice passed validation.
        """

        errors = []

        # ---------------------------------------------------------
        # 1. Validate invoice total
        # ---------------------------------------------------------
        #
        # Check:
        #
        # subtotal + GST = total
        #
        # We only perform this check when all three values
        # are available.
        #
        if (
            invoice.subtotal is not None
            and invoice.gst is not None
            and invoice.total is not None
        ):
            expected_total = invoice.subtotal + invoice.gst

            # Allow a small rounding difference.
            if abs(expected_total - invoice.total) > 0.01:
                errors.append(
                    f"Invoice total mismatch: "
                    f"expected {expected_total}, "
                    f"but got {invoice.total}"
                )

        # ---------------------------------------------------------
        # 2. Validate individual invoice items
        # ---------------------------------------------------------

        for index, item in enumerate(invoice.items):

            # Human-readable item number.
            item_number = index + 1

            # -----------------------------------------------------
            # Check quantity
            # -----------------------------------------------------

            if item.quantity is None:
                errors.append(
                    f"Item {item_number} is missing quantity."
                )

            # -----------------------------------------------------
            # Check unit price
            # -----------------------------------------------------

            if item.unit_price is None:
                errors.append(
                    f"Item {item_number} is missing unit price."
                )

            # -----------------------------------------------------
            # Check amount
            # -----------------------------------------------------

            if item.amount is None:
                errors.append(
                    f"Item {item_number} is missing amount."
                )

            # -----------------------------------------------------
            # Validate:
            #
            # quantity × unit_price = amount
            #
            # Only perform the calculation when all three
            # values are available.
            # -----------------------------------------------------

            if (
                item.quantity is not None
                and item.unit_price is not None
                and item.amount is not None
            ):
                expected_amount = (
                    item.quantity * item.unit_price
                )

                # Allow a small rounding difference.
                if abs(expected_amount - item.amount) > 0.01:
                    errors.append(
                        f"Item {item_number} amount mismatch: "
                        f"expected {expected_amount}, "
                        f"but got {item.amount}"
                    )

        # Return all validation errors.
        #
        # [] means all business validations passed.
        return errors

    def find_duplicate_items(
        self,
        invoice: Invoice
    ) -> list[str]:
        """
        Detect duplicate invoice line-item descriptions.

        This is a simple rule for our learning project.
        """

        seen = set()
        duplicates = []

        for item in invoice.items:

            # Ignore items without a description.
            if not item.description:
                continue

            # Normalize capitalization and whitespace
            # before checking for duplicates.
            description = item.description.strip().lower()

            if description in seen:
                duplicates.append(
                    f"Duplicate line item detected: "
                    f"{item.description}"
                )
            else:
                seen.add(description)

        return duplicates