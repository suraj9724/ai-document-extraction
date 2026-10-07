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
        # If both subtotal and GST are available,
        # check whether:
        #
        # subtotal + GST = total
        #
        if (
            invoice.subtotal is not None
            and invoice.gst is not None
            and invoice.total is not None
        ):
            expected_total = invoice.subtotal + invoice.gst

            # We allow a very small difference because
            # floating-point calculations can have tiny
            # rounding differences.
            if abs(expected_total - invoice.total) > 0.01:
                errors.append(
                    f"Invoice total mismatch: "
                    f"expected {expected_total}, "
                    f"but got {invoice.total}"
                )

        # ---------------------------------------------------------
        # 2. Validate individual invoice items
        # ---------------------------------------------------------
        #
        # For every item we check:
        #
        # quantity × unit_price = amount
        #

        for index, item in enumerate(invoice.items):

            # We can only calculate the expected amount
            # when both quantity and unit price are available.
            if (
                item.quantity is not None
                and item.unit_price is not None
                and item.amount is not None
            ):

                expected_amount = (
                    item.quantity * item.unit_price
                )

                # Compare calculated amount with extracted amount.
                if abs(
                    expected_amount - item.amount
                ) > 0.01:

                    errors.append(
                        f"Item {index + 1} amount mismatch: "
                f"expected {expected_amount}, "
                f"but got {item.amount}"
            )

        # ---------------------------------------------------------
        # 3. Validate subtotal
        # ---------------------------------------------------------
        #
        # If items are available, calculate their total
        # and compare it with the extracted subtotal.
        #
        if invoice.items and invoice.subtotal is not None:

            calculated_subtotal = sum(
                item.amount
                for item in invoice.items
            )

            if abs(
                calculated_subtotal - invoice.subtotal
            ) > 0.01:
                errors.append(
                    f"Subtotal mismatch: "
                    f"expected {calculated_subtotal}, "
                    f"but got {invoice.subtotal}"
                )

        # Return all validation errors.
        #
        # [] means everything passed.
        return errors