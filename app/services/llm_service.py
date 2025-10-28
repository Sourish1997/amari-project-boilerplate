import json
from typing import Any

import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def extract_fields_from_documents(document_data: dict[str, Any]) -> dict[str, Any]:
    """
    Use LLM to extract specific fields from document text.

    Args:
        document_data: Dictionary containing document text and metadata

    Returns:
        dict[str, Any]: Extracted fields in JSON format
    """

    prompt = f"""
Extract the following specific fields from the provided document data and return them in JSON format.

Required fields to extract:
- Bill of lading number
- Container Number  
- Consignee Name
- Consignee Address
- Date of export
- Line Items Count
- Number of Packages
- Gross Weight (total weight)
- Average Price

Document data:
{json.dumps(document_data, indent=2)}

IMPORTANT: Return ONLY the raw JSON object without any markdown formatting, code blocks, or additional text. Do not wrap the response in ```json or any other formatting. Use null for any fields that cannot be found or determined.

Return exactly this format (raw JSON only):
{{
    "bill_of_lading_number": "value or null",
    "container_number": "value or null", 
    "consignee_name": "value or null",
    "consignee_address": "value or null",
    "date_of_export": "value or null",
    "line_items_count": "value or null",
    "no_of_packages": "value or null",
    "gross_weight": "value or null",
    "average_price": "value or null"
}}
"""
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=500,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        response_text = response.content[0].text.strip()

        # Handle markdown-wrapped JSON by extracting content between ```json and ```
        if response_text.startswith("```json") and response_text.endswith("```"):
            # Extract JSON from markdown code block
            json_content = response_text[7:-3].strip()  # Remove ```json and ```
        elif response_text.startswith("```") and response_text.endswith("```"):
            # Extract JSON from plain code block
            lines = response_text.split("\n")
            json_content = "\n".join(
                lines[1:-1]
            ).strip()  # Remove first and last line (```)
        else:
            # Use response as-is
            json_content = response_text

        # Parse the JSON response
        extracted_data = json.loads(json_content)

        # Add computed average_gross_weight field
        if extracted_data.get("no_of_packages") and extracted_data.get("gross_weight"):
            try:
                # Extract numeric value from no_of_packages
                no_of_packages_str = str(extracted_data["no_of_packages"]).strip()
                no_of_packages = float(
                    "".join(
                        filter(lambda x: x.isdigit() or x == ".", no_of_packages_str)
                    )
                )

                # Extract numeric value from gross_weight (handle cases like "16250.000 KGS")
                gross_weight_str = str(extracted_data["gross_weight"]).strip()
                # Remove common weight units and extract numeric part
                gross_weight_clean = (
                    gross_weight_str.upper()
                    .replace("KGS", "")
                    .replace("KG", "")
                    .replace("LBS", "")
                    .replace("LB", "")
                    .strip()
                )
                gross_weight = float(
                    "".join(
                        filter(lambda x: x.isdigit() or x == ".", gross_weight_clean)
                    )
                )

                if no_of_packages > 0:
                    extracted_data["average_gross_weight"] = str(
                        gross_weight / no_of_packages
                    )
                else:
                    extracted_data["average_gross_weight"] = None
            except (ValueError, TypeError):
                extracted_data["average_gross_weight"] = None
        else:
            extracted_data["average_gross_weight"] = None

        return extracted_data
    except json.JSONDecodeError:
        # If JSON parsing fails, return a structured error response
        return {
            "bill_of_lading_number": None,
            "container_number": None,
            "consignee_name": None,
            "consignee_address": None,
            "date_of_export": None,
            "line_items_count": None,
            "no_of_packages": None,
            "gross_weight": None,
            "average_gross_weight": None,
            "average_price": None,
            "error": "Failed to parse LLM response as JSON",
            "raw_response": response.content[0].text.strip(),
        }
