import re


class InvoiceNormalizer:

    def normalize(self, data: dict) -> dict:
        """
        Normalize common formatting differences in LLM output
        before sending the data to Pydantic.

        Example:

        "$2,400.00" -> 2400.0
        "qty"        -> "quantity"
        "service"    -> "description"
        """

        # ---------------------------------------------------------
        # 1. Normalize invoice-level monetary values
        # ---------------------------------------------------------

        for field in ["subtotal", "gst", "total"]:

            # Only normalize the field if it exists
            # in the LLM response.
            if field in data:
                data[field] = self._to_number(
                    data[field]
                )

        # ---------------------------------------------------------
        # 2. Normalize invoice items
        # ---------------------------------------------------------

        items = data.get("items", [])

        normalized_items = []

        for item in items:
            normalized_item = {}

            description = (
                item.get("description")
                or item.get("service")
                or item.get("product")
                or item.get("item")
            )
            normalized_item["description"] = description

            quantity = (
                item.get("quantity")
                if item.get("quantity") is not None
                else item.get("qty")
            )
            normalized_item["quantity"] = self._to_number(quantity)

            unit_price = (
                item.get("unit_price")
                if item.get("unit_price") is not None
                else item.get("price")
            )

            if unit_price is None:
                unit_price = item.get("rate")

            normalized_item["unit_price"] = self._to_number(unit_price)

            amount = (
                item.get("amount")
                if item.get("amount") is not None
                else item.get("total")
            )
            if amount is None:
                amount = item.get("line_total")

            normalized_item["amount"] = self._to_number(amount)

            # Preserve the page number returned by the LLM.
            normalized_item["page"] = item.get("page")

            normalized_items.append(normalized_item)

        # Replace the original items with normalized items
        data["items"] = normalized_items

        return data

    @staticmethod
    def _to_number(value):
        """
        Convert common numeric formats into float.

        Examples:

        100          -> 100.0
        "100"        -> 100.0
        "$2,400.00"  -> 2400.0
        "₹4,500.50"  -> 4500.5
        """

        # Missing values should remain None.
        if value is None:
            return None

        # If it's already a number, convert it to float.
        if isinstance(value, (int, float)):
            return float(value)

        # Convert other values to strings so we can
        # remove currency symbols and commas.
        value = str(value).strip()

        # Remove everything except digits,
        # decimal point and minus sign.
        value = re.sub(
            r"[^0-9.\-]",
            "",
            value
        )

        # If nothing useful remains, return None.
        if not value:
            return None

        return float(value)