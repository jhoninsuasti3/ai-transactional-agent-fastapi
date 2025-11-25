#!/usr/bin/env python3
"""Test script for transactional agent tools.

Tests all 4 required tools:
1. format_phone_number_tool
2. validate_transaction_tool
3. execute_transaction_tool
4. get_transaction_status_tool
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from apps.agents.transactional.tools import (
    format_phone_number_tool,
    validate_transaction_tool,
    execute_transaction_tool,
    get_transaction_status_tool,
)


def test_format_phone():
    """Test phone number formatting."""
    print("=" * 60)
    print("🧪 Testing format_phone_number_tool")
    print("=" * 60)

    # Test cases
    test_cases = [
        ("3001234567", True, "Valid phone"),
        ("300-123-4567", True, "Phone with dashes"),
        ("(300) 123-4567", True, "Phone with parentheses"),
        ("123456", False, "Too short"),
        ("30012345678", False, "Too long"),
        ("4001234567", False, "Doesn't start with 3"),
    ]

    for phone, should_be_valid, description in test_cases:
        print(f"\n📱 Test: {description}")
        print(f"   Input: {phone}")
        result = format_phone_number_tool.invoke({"phone": phone})
        print(f"   Result: {result}")

        if should_be_valid:
            assert result["valid"], f"Expected valid but got invalid for {phone}"
            print("   ✅ PASS")
        else:
            assert not result["valid"], f"Expected invalid but got valid for {phone}"
            print("   ✅ PASS")

    print("\n" + "=" * 60)
    print("✅ All format_phone_number_tool tests passed!")
    print("=" * 60)


def test_mock_api_connection():
    """Test connection to Mock API."""
    print("\n" + "=" * 60)
    print("🧪 Testing Mock API Connection")
    print("=" * 60)

    print("\n⚠️  Assuming Mock API is running on http://localhost:8000")
    print("   If not, run: docker compose up -d mock-api")

    # Test validation
    print("\n📞 Testing validate_transaction_tool...")
    result = validate_transaction_tool.invoke({
        "phone": "3001234567",
        "amount": 50000.0
    })
    print(f"   Result: {result}")

    if "error" in result:
        print(f"   ❌ FAIL: {result['error']}")
        print("\n   💡 Check if Mock API is running:")
        print("      docker compose ps mock-api")
        return False
    else:
        print("   ✅ PASS")

    # Test execution (if validation succeeded)
    if result.get("valid"):
        print("\n💸 Testing execute_transaction_tool...")
        exec_result = execute_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 50000.0,
            "validation_id": result.get("validation_id")
        })
        print(f"   Result: {exec_result}")

        if "error" in exec_result:
            print(f"   ❌ FAIL: {exec_result['error']}")
            return False
        else:
            print("   ✅ PASS")

        # Test status query (if execution succeeded)
        if exec_result.get("success"):
            transaction_id = exec_result.get("transaction_id")
            if transaction_id:
                print(f"\n🔍 Testing get_transaction_status_tool...")
                status_result = get_transaction_status_tool.invoke({
                    "transaction_id": transaction_id
                })
                print(f"   Result: {status_result}")

                if "error" in status_result:
                    print(f"   ❌ FAIL: {status_result['error']}")
                    return False
                else:
                    print("   ✅ PASS")

    print("\n" + "=" * 60)
    print("✅ All Mock API tools tests passed!")
    print("=" * 60)
    return True


def main():
    """Run all tests."""
    print("\n" + "🚀" * 30)
    print("TESTING TRANSACTIONAL AGENT TOOLS")
    print("🚀" * 30 + "\n")

    try:
        # Test 1: Phone formatting (no API needed)
        test_format_phone()

        # Test 2: Mock API tools
        api_tests_passed = test_mock_api_connection()

        if api_tests_passed:
            print("\n" + "🎉" * 30)
            print("ALL TESTS PASSED!")
            print("🎉" * 30 + "\n")
        else:
            print("\n⚠️  Some tests failed. Check Mock API status.")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
