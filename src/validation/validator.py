from extraction.schema import Invoice
from validation.review import ReviewField


class InvoiceValidator:

    def validate(self, invoice: Invoice) -> list[ReviewField]:
        """
        Validate the extracted invoice using business rules.

        Returns structured review information so that the
        caller knows which field caused the validation issue.
        """

        errors = []

        # ---------------------------------------------------------
        # 1. Validate invoice total
        # ---------------------------------------------------------

        if (
            invoice.subtotal is not None
            and invoice.gst is not None
            and invoice.total is not None
        ):
            expected_total = invoice.subtotal + invoice.gst

            if abs(expected_total - invoice.total) > 0.01:
                errors.append(
                    ReviewField(
                        field="total",
                        value=invoice.total,
                        reason=(
                            f"Invoice total mismatch: "
                            f"expected {expected_total}, "
                            f"but got {invoice.total}"
                        ),
                    )
                )

        # ---------------------------------------------------------
        # 2. Validate individual invoice items
        # ---------------------------------------------------------

        for index, item in enumerate(invoice.items):

            item_number = index + 1

            # Missing quantity
            if item.quantity is None:
                errors.append(
                    ReviewField(
                        field=f"items[{index}].quantity",
                        value=None,
                        page=item.page,
                        reason=(
                            f"Item {item_number} is missing quantity."
                        ),
                    )
                )

            # Missing unit price
            if item.unit_price is None:
                errors.append(
                    ReviewField(
                        field=f"items[{index}].unit_price",
                        value=None,
                        page=item.page,
                        reason=(
                            f"Item {item_number} "
                            f"is missing unit price."
                        ),
                    )
                )

            # Missing amount
            if item.amount is None:
                errors.append(
                    ReviewField(
                        field=f"items[{index}].amount",
                        value=None,
                        page=item.page,
                        reason=(
                            f"Item {item_number} is missing amount."
                        ),
                    )
                )

            # -----------------------------------------------------
            # quantity × unit_price = amount
            # -----------------------------------------------------

            if (
                item.quantity is not None
                and item.unit_price is not None
                and item.amount is not None
            ):
                expected_amount = (
                    item.quantity * item.unit_price
                )

                if abs(expected_amount - item.amount) > 0.01:
                    errors.append(
                        ReviewField(
                            field=f"items[{index}].amount",
                            value=item.amount,
                            page=item.page,
                            reason=(
                                f"Item {item_number} amount mismatch: "
                                f"expected {expected_amount}, "
                                f"but got {item.amount}"
                            ),
                        )
                    )

        return errors

    def find_duplicate_items(
        self,
        invoice: Invoice
    ) -> list[ReviewField]:
        """
        Detect duplicate invoice line-item descriptions.
        """

        seen = set()
        duplicates = []

        for index, item in enumerate(invoice.items):

            if not item.description:
                continue

            description = item.description.strip().lower()

            if description in seen:
                duplicates.append(
                    ReviewField(
                        field=f"items[{index}].description",
                        value=item.description,
                        page=item.page,
                        reason=(
                            f"Duplicate line item detected: "
                            f"{item.description}"
                        ),
                    )
                )
            else:
                seen.add(description)

        return duplicates