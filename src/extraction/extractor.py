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

The JSON must follow this structure:

{{
    "invoice_number": null,
    "invoice_date": null,

    "seller": {{
        "name": null,
        "city": null,
        "state": null
    }},

    "customer": {{
        "name": null,
        "city": null,
        "state": null
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