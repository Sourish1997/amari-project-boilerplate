import json
from unittest.mock import Mock, patch

from app.services.llm_service import extract_fields_from_documents


class TestLLMService:
    @patch("app.services.llm_service.client")
    def test_extract_fields_from_documents_success(self, mock_client):
        """Test successful field extraction from documents."""
        # Mock response from Anthropic
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = json.dumps(
            {
                "bill_of_lading_number": "BL123456789",
                "container_number": "CONT987654321",
                "consignee_name": "ABC Trading Company",
                "consignee_address": "123 Main St, New York, NY 10001",
                "date_of_export": "2024-01-15",
                "line_items_count": "5",
                "average_gross_weight": "1500 kg",
                "average_price": "$2500.00",
            }
        )

        mock_client.messages.create.return_value = mock_response

        # Sample document data
        document_data = {
            "sample.pdf": "Bill of Lading BL123456789 Container CONT987654321...",
            "sample.xlsx": [
                ["Item", "Weight"],
                ["Product A", "300kg"],
                ["Product B", "400kg"],
            ],
        }

        result = extract_fields_from_documents(document_data)

        # Verify the function called the API correctly
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args

        assert call_args[1]["model"] == "claude-3-sonnet-20240229"
        assert call_args[1]["max_tokens"] == 500
        assert call_args[1]["temperature"] == 0.1

        # Verify the result
        assert isinstance(result, dict)
        assert result["bill_of_lading_number"] == "BL123456789"
        assert result["container_number"] == "CONT987654321"
        assert result["consignee_name"] == "ABC Trading Company"
        assert result["date_of_export"] == "2024-01-15"
        assert result["line_items_count"] == "5"

    @patch("app.services.llm_service.client")
    def test_extract_fields_json_parse_error(self, mock_client):
        """Test handling of invalid JSON response."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "This is not valid JSON response"

        mock_client.messages.create.return_value = mock_response

        document_data = {"test.pdf": "Sample document text"}

        result = extract_fields_from_documents(document_data)

        # Verify error handling
        assert isinstance(result, dict)
        assert result["bill_of_lading_number"] is None
        assert result["container_number"] is None
        assert result["consignee_name"] is None
        assert result["consignee_address"] is None
        assert result["date_of_export"] is None
        assert result["line_items_count"] is None
        assert result["average_gross_weight"] is None
        assert result["average_price"] is None
        assert result["error"] == "Failed to parse LLM response as JSON"
        assert result["raw_response"] == "This is not valid JSON response"

    def test_extract_fields_prompt_structure(self):
        """Test that the prompt contains required fields."""
        with patch("app.services.llm_service.client") as mock_client:
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = json.dumps(
                {
                    "bill_of_lading_number": None,
                    "container_number": None,
                    "consignee_name": None,
                    "consignee_address": None,
                    "date_of_export": None,
                    "line_items_count": None,
                    "average_gross_weight": None,
                    "average_price": None,
                }
            )

            mock_client.messages.create.return_value = mock_response

            document_data = {"test.pdf": "Sample text"}
            extract_fields_from_documents(document_data)

            # Get the prompt that was sent
            call_args = mock_client.messages.create.call_args
            prompt = call_args[1]["messages"][0]["content"]

            # Verify all required fields are mentioned in the prompt
            assert "Bill of lading number" in prompt
            assert "Container Number" in prompt
            assert "Consignee Name" in prompt
            assert "Consignee Address" in prompt
            assert "Date of export" in prompt
            assert "Line Items Count" in prompt
            assert "Average Gross Weight" in prompt
            assert "Average Price" in prompt
            assert "JSON" in prompt
