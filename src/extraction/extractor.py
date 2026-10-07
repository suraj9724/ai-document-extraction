import json

from ollama import Client

from extraction.schema import Invoice


class InvoiceExtractor:

    def __init__(
        self,
        model: str = "llama3.2:3b"
    ):
        self.model = model
        self.client = Client(
            host="http://localhost:11434"
        )

    def extract(self, document_text: str) -> Invoice:

        prompt = f"""
You are an information extraction system.

Extract invoice information from the document
and return ONLY valid JSON.

Do not explain anything.

If a field is missing, use null.

The JSON must follow this structure:

{{
    "invoice_number": null,
    "invoice_date": null,

    "seller": {{
        "name": "",
        "city": null,
        "state": null
    }},

    "customer": {{
        "name": "",
        "city": null,
        "state": null
    }},

    "items": [
        {{
            "description": "",
            "quantity": 0,
            "unit_price": 0,
            "amount": 0
        }}
    ],

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

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response["message"]["content"].strip()

        data = json.loads(content)

        return Invoice.model_validate(data)