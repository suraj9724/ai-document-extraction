import json

from ollama import Client

from extraction.schema import Invoice
from extraction.normalizer import InvoiceNormalizer


class InvoiceExtractor:

    def __init__(
        self,
        model: str = "llama3.2:3b"
    ):
        # Store the model name so we can easily change it later
        self.model = model

        # Connect to the local Ollama server
        self.client = Client(
            host="http://localhost:11434"
        )

        self.normalizer = InvoiceNormalizer()

    def extract(self, document_text: str) -> Invoice:

        # This prompt tells the LLM exactly what
        # information we want to extract.
        prompt = f"""
You are an invoice information extraction system.

Extract information from the document below.

Return ONLY valid JSON.

IMPORTANT RULES:

1. Extract information only when it is explicitly
   present in the document.

2. NEVER invent missing information.

3. NEVER guess a value.

4. If a field cannot be found, return null.

5. Do not calculate missing values.

6. Preserve the values found in the document.

7. For invoice items, extract every item that is
   explicitly present.

8. Return an empty array if no invoice items
   can be found.
   
IMPORTANT LINE ITEM RULES:

9. For each invoice item, carefully distinguish:
   - quantity
   - unit_price
   - amount

10. If an item shows a pattern such as:
    2 × $450 = $900

    then:
    quantity = 2
    unit_price = 450
    amount = 900

11. NEVER use the line amount as the unit price.

12. If quantity, unit price, and amount are all explicitly
    present, preserve each value exactly as shown.

13. Do not calculate unit_price from amount / quantity.
    Only extract the value explicitly shown in the document.

14. Before returning the JSON, verify that the extracted
    quantity, unit_price, and amount correspond to the
    same line item.

15. For every invoice item, include the page number where
    that item appears.

16. The page number must correspond to the [PAGE X] marker
    provided in the document.

17. Do not guess the page number.

18. If the page cannot be determined, return null.

19. If invoice items continue across multiple pages,
    preserve every item and assign each item its correct page.
    
IMPORTANT ITEM EXTRACTION RULES:

20. The "items" array must contain ONLY actual invoice
    line items representing products or services.

21. Do NOT include invoice totals or summary rows as items.

22. Do NOT include:
    - Subtotal
    - GST / Tax
    - Total
    - Additional Services Subtotal
    - Additional GST
    - Additional Services Total
    - Payment Terms
    - Bank Details
    - Notes
    - Terms and Conditions
    - Payment instructions

23. An item should normally have a description and at least
    one monetary/quantity value associated with it.

24. Summary or informational text must never be represented
    as an invoice item.

25. If a section contains additional services with actual
    line items, extract those line items, but do not extract
    the section's subtotal, tax, or total as an item.
    
26. When an address contains city, state/province,
    postal code, and country, separate them into the
    appropriate fields.

27. Do not put the country inside city or state.

Example:

"Ahmedabad, Gujarat 380015, India"

must become:

city = "Ahmedabad"
state = "Gujarat"
country = "India"

IMPORTANT DISTINCTION:

26. Invoice-level financial totals must still be extracted
    into their dedicated fields.

27. Do NOT put these values inside the "items" array.

28. Extract:
    - Subtotal → "subtotal"
    - GST / Tax → "gst"
    - Final invoice total → "total"

29. The following are NOT invoice items, but their values
    should still be extracted when they represent the
    invoice-level totals:
    - Subtotal
    - GST
    - Tax
    - Total
    - Invoice Total

30. If the document contains additional section totals,
    do not confuse them with the main invoice-level totals.
    Only use the totals that clearly correspond to the
    main invoice total.
    
    31. If a country is explicitly present in a party address,
    extract it into the "country" field.

32. Example:

    "Ahmedabad, Gujarat 380015, India"

    must become:

    city = "Ahmedabad"
    state = "Gujarat"
    country = "India"

33. Example:

    "Melbourne, VIC 3000, Australia"

    must become:

    city = "Melbourne"
    state = "VIC"
    country = "Australia"

34. Do not omit the country when it is explicitly present.

The JSON must follow this structure:

{{
    "invoice_number": null,
    "invoice_date": null,

    "seller": {{
        "name": null,
        "city": null,
        "state": null,
        "country":null
    }},

    "customer": {{
        "name": null,
        "city": null,
        "state": null,
        "country": null
    }},

    "items": [],

    "subtotal": null,
    "gst": null,
    "total": null
}}

Document:
========================

{document_text}

========================

Return ONLY JSON.
"""

        # Send the extraction request to the local LLM
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Get the text returned by the LLM
        content = response["message"]["content"].strip()

        # Convert JSON text into a Python dictionary
        data = json.loads(content)

        # Normalize invoice data before validation
        data = self.normalizer.normalize(data)

        # Validate the structure using our Pydantic schema
        return Invoice.model_validate(data)