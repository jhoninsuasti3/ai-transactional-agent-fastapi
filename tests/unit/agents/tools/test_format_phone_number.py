"""Tests for format_phone_number tool."""

import pytest

from apps.agents.transactional.tools.format_phone_number import format_phone_number_tool


@pytest.mark.unit
class TestFormatPhoneNumberTool:
    """Test suite for format_phone_number_tool."""

    def test_valid_10_digit_phone(self):
        """Test valid 10-digit phone number."""
        result = format_phone_number_tool.invoke({"phone": "3001234567"})
        assert result["valid"] is True
        assert result["formatted_phone"] == "3001234567"

    def test_phone_with_spaces(self):
        """Test phone number with spaces."""
        result = format_phone_number_tool.invoke({"phone": "300 123 4567"})
        assert result["valid"] is True
        assert result["formatted_phone"] == "3001234567"

    def test_phone_with_dashes(self):
        """Test phone number with dashes."""
        result = format_phone_number_tool.invoke({"phone": "300-123-4567"})
        assert result["valid"] is True
        assert result["formatted_phone"] == "3001234567"

    def test_phone_with_parentheses(self):
        """Test phone number with parentheses."""
        result = format_phone_number_tool.invoke({"phone": "(300) 123-4567"})
        assert result["valid"] is True
        assert result["formatted_phone"] == "3001234567"

    def test_phone_with_country_code(self):
        """Test phone number with +57 country code - should fail (12 digits)."""
        result = format_phone_number_tool.invoke({"phone": "+573001234567"})
        assert result["valid"] is False  # 12 digits total

    def test_phone_with_country_code_no_plus(self):
        """Test phone number with 57 country code without plus - should fail (12 digits)."""
        result = format_phone_number_tool.invoke({"phone": "573001234567"})
        assert result["valid"] is False  # 12 digits total

    def test_phone_too_short(self):
        """Test phone number with less than 10 digits."""
        result = format_phone_number_tool.invoke({"phone": "12345"})
        assert result["valid"] is False
        assert "10 dígitos" in result["error"]

    def test_phone_too_long(self):
        """Test phone number with more than 10 digits (without country code)."""
        result = format_phone_number_tool.invoke({"phone": "12345678901"})
        assert result["valid"] is False

    def test_phone_with_letters(self):
        """Test phone number with letters."""
        result = format_phone_number_tool.invoke({"phone": "300ABC4567"})
        assert result["valid"] is False
        assert "10 dígitos" in result["error"]

    def test_empty_phone(self):
        """Test empty phone number."""
        result = format_phone_number_tool.invoke({"phone": ""})
        assert result["valid"] is False

    def test_none_phone(self):
        """Test None phone number."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            format_phone_number_tool.invoke({"phone": None})

    def test_phone_with_special_characters(self):
        """Test phone with various special characters."""
        result = format_phone_number_tool.invoke({"phone": "300.123.4567"})
        assert result["valid"] is True
        assert result["formatted_phone"] == "3001234567"

    def test_mobile_numbers_common_prefixes(self):
        """Test common Colombian mobile prefixes."""
        prefixes = [
            "300",
            "301",
            "302",
            "310",
            "311",
            "312",
            "313",
            "314",
            "315",
            "316",
            "317",
            "318",
            "319",
            "320",
            "321",
            "322",
            "323",
            "350",
            "351",
        ]

        for prefix in prefixes:
            result = format_phone_number_tool.invoke({"phone": f"{prefix}1234567"})
            assert result["valid"] is True, f"Prefix {prefix} should be valid"
            assert result["formatted_phone"] == f"{prefix}1234567"

    def test_phone_not_starting_with_3(self):
        """Test phone number not starting with 3."""
        result = format_phone_number_tool.invoke({"phone": "2001234567"})
        assert result["valid"] is False
        assert "debe comenzar con 3" in result["error"]
