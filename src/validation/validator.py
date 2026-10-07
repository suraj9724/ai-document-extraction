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
        # Validate individual invoice items
        # ---------------------------------------------------------

        for index, item in enumerate(invoice.items):

            # Create a human-readable item number.
            item_number = index + 1

            # -----------------------------------------------------
            # Check whether quantity exists
            # -----------------------------------------------------

            if item.quantity is None:

                errors.append(
                    f"Item {item_number} is missing quantity."
                )

            # -----------------------------------------------------
            # Check whether unit price exists
            # -----------------------------------------------------

            if item.unit_price is None:

                errors.append(
                    f"Item {item_number} is missing unit price."
                )

            # -----------------------------------------------------
            # Check whether amount exists
            # -----------------------------------------------------

            if item.amount is None:

                errors.append(
                    f"Item {item_number} is missing amount."
                )

            # -----------------------------------------------------
            # Validate the mathematical relationship
            # -----------------------------------------------------
            #
            # We only perform this calculation when all three
            # values are available.
            #

            if (
                item.quantity is not None
                and item.unit_price is not None
                and item.amount is not None
            ):

                expected_amount = (
                    item.quantity * item.unit_price
                )

                # Allow a tiny rounding difference.
                if abs(
                    expected_amount - item.amount
                ) > 0.01:

                    errors.append(
                        f"Item {item_number} amount mismatch: "
                        f"expected {expected_amount}, "
                        f"but got {item.amount}"
                    )
                    
        # ---------------------------------------------------------
        # Validate subtotal against line-item amounts
        # ---------------------------------------------------------

        if invoice.items and invoice.subtotal is not None:

            # Check whether every item has an amount.
            all_amounts_available = all(
                item.amount is not None
                for item in invoice.items
            )

            # We can only calculate the subtotal when
            # every line item has an amount.
            if all_amounts_available:

                calculated_subtotal = sum(
                    item.amount
                    for item in invoice.items
                )

                # Compare calculated subtotal with the
                # subtotal extracted from the invoice.
                if abs(
                    calculated_subtotal - invoice.subtotal
                ) > 0.01:
                    errors.append(
                        f"Subtotal mismatch: "
                        f"line items total "
                        f"{calculated_subtotal}, "
                        f"but invoice subtotal is "
                        f"{invoice.subtotal}"
                    )

        # ---------------------------------------------------------
        # 3. Validate subtotal
        # ---------------------------------------------------------
        #
        # If items are available, calculate their total
        # and compare it with the extracted subtotal.
        #
        if invoice.items and invoice.subtotal is not None:

            # We can only calculate the subtotal if every item
            # has an extracted amount.
            #
            # If even one amount is missing, we don't have
            # enough information to perform this calculation.
            all_amounts_available = all(
                item.amount is not None
                for item in invoice.items
            )

            if all_amounts_available:

                # Add all extracted item amounts together.
                calculated_subtotal = sum(
                    item.amount
                    for item in invoice.items
                )

                # Compare our calculated subtotal with the
                # subtotal extracted by the LLM.
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
    
    
    def find_duplicate_items(self, invoice: Invoice) -> list[str]:
        """
        Detect duplicate line-item descriptions.

        This is a simple check for our learning project.
        """

        seen = set()
        duplicates = []

        for item in invoice.items:

            # Ignore items without a description.
            if not item.description:
                continue

            # Normalize the description so that differences
            # in capitalization don't create false differences.
            description = item.description.strip().lower()

            if description in seen:

                duplicates.append(
                    f"Duplicate line item detected: "
                    f"{item.description}"
                )

            else:

                seen.add(description)

        return duplicates