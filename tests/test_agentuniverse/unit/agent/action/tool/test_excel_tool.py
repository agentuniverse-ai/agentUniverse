#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Excel Tool Test Script
Tests all four modes: read, write, append, info
"""

import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentuniverse.agent.action.tool.common_tool.excel_tool import ExcelTool


def print_result(title: str, result: str):
    """Pretty print test results"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    result_dict = json.loads(result)
    print(json.dumps(result_dict, indent=2, ensure_ascii=False))
    return result_dict


def test_excel_tool():
    """Test all Excel tool operations"""
    print("🧪 Starting Excel Tool Tests...")

    tool = ExcelTool()
    test_file = "/tmp/test_excel_tool_data.xlsx"

    # Clean up any existing test file
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"✅ Cleaned up existing test file: {test_file}")

    # Test 1: Write new Excel file
    print("\n📝 Test 1: Writing new Excel file...")
    test_data = [
        ["Name", "Age", "City", "Score"],
        ["Alice", 25, "New York", 95],
        ["Bob", 30, "San Francisco", 88],
        ["Charlie", 35, "Los Angeles", 92],
        ["David", 28, "Chicago", 87]
    ]

    result1 = tool.execute(
        file_path=test_file,
        mode="write",
        data=test_data,
        sheet_name="Students",
        overwrite=True
    )
    result1_dict = print_result("Test 1: Write Operation", result1)

    assert result1_dict["status"] == "success", "Write operation failed"
    assert result1_dict["rows_written"] == 5, "Wrong number of rows written"
    print("✅ Test 1 PASSED")

    # Test 2: Read Excel file
    print("\n📖 Test 2: Reading Excel file...")
    result2 = tool.execute(
        file_path=test_file,
        mode="read",
        sheet_name="Students"
    )
    result2_dict = print_result("Test 2: Read Operation", result2)

    assert result2_dict["status"] == "success", "Read operation failed"
    assert result2_dict["rows_read"] == 5, "Wrong number of rows read"
    assert len(result2_dict["data"]) == 5, "Data length mismatch"
    print("✅ Test 2 PASSED")

    # Test 3: Get file info
    print("\n📊 Test 3: Getting file info...")
    result3 = tool.execute(
        file_path=test_file,
        mode="info"
    )
    result3_dict = print_result("Test 3: Info Operation", result3)

    assert result3_dict["status"] == "success", "Info operation failed"
    assert result3_dict["total_sheets"] == 1, "Wrong number of sheets"
    assert "Students" in result3_dict["sheet_names"], "Sheet name not found"
    print("✅ Test 3 PASSED")

    # Test 4: Append data
    print("\n➕ Test 4: Appending data to file...")
    append_data = [
        ["Eve", 27, "Seattle", 91],
        ["Frank", 32, "Boston", 89]
    ]

    result4 = tool.execute(
        file_path=test_file,
        mode="append",
        data=append_data,
        sheet_name="Students"
    )
    result4_dict = print_result("Test 4: Append Operation", result4)

    assert result4_dict["status"] == "success", "Append operation failed"
    assert result4_dict["rows_appended"] == 2, "Wrong number of rows appended"
    print("✅ Test 4 PASSED")

    # Test 5: Read again to verify append
    print("\n🔍 Test 5: Verifying appended data...")
    result5 = tool.execute(
        file_path=test_file,
        mode="read",
        sheet_name="Students"
    )
    result5_dict = print_result("Test 5: Read After Append", result5)

    assert result5_dict["status"] == "success", "Read after append failed"
    assert result5_dict["rows_read"] == 7, f"Expected 7 rows, got {result5_dict['rows_read']}"
    assert result5_dict["data"][-1][0] == "Frank", "Last row data mismatch"
    print("✅ Test 5 PASSED")

    # Test 6: Read with max_rows limit
    print("\n📏 Test 6: Reading with row limit...")
    result6 = tool.execute(
        file_path=test_file,
        mode="read",
        sheet_name="Students",
        max_rows=3
    )
    result6_dict = print_result("Test 6: Read with Limit", result6)

    assert result6_dict["status"] == "success", "Limited read failed"
    assert result6_dict["rows_read"] == 3, "Row limit not applied correctly"
    print("✅ Test 6 PASSED")

    # Test 7: Security - Try to write to forbidden directory
    print("\n🔒 Test 7: Testing security validation...")
    result7 = tool.execute(
        file_path="/etc/passwd.xlsx",
        mode="write",
        data=[["test"]]
    )
    result7_dict = print_result("Test 7: Security Check", result7)

    assert result7_dict["status"] == "error", "Security validation should fail"
    assert "Access denied" in result7_dict["error"], "Expected access denied error"
    print("✅ Test 7 PASSED - Security working correctly")

    # Test 8: Error handling - Invalid mode
    print("\n❌ Test 8: Testing error handling (invalid mode)...")
    result8 = tool.execute(
        file_path=test_file,
        mode="invalid_mode"
    )
    result8_dict = print_result("Test 8: Invalid Mode", result8)

    assert result8_dict["status"] == "error", "Should return error for invalid mode"
    assert "Invalid mode" in result8_dict["error"], "Expected invalid mode error"
    print("✅ Test 8 PASSED - Error handling working correctly")

    # Test 9: Error handling - Missing required parameter
    print("\n❌ Test 9: Testing error handling (missing data)...")
    result9 = tool.execute(
        file_path="/tmp/test_new.xlsx",
        mode="write"
        # Missing 'data' parameter
    )
    result9_dict = print_result("Test 9: Missing Parameter", result9)

    assert result9_dict["status"] == "error", "Should return error for missing data"
    assert "required" in result9_dict["error"].lower(), "Expected parameter required error"
    print("✅ Test 9 PASSED - Parameter validation working correctly")

    # Clean up test file
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\n🧹 Cleaned up test file: {test_file}")

    print("\n" + "="*60)
    print("  🎉 ALL TESTS PASSED!")
    print("="*60)
    print("\nExcel Tool Summary:")
    print("  ✅ Write operation")
    print("  ✅ Read operation")
    print("  ✅ Append operation")
    print("  ✅ Info operation")
    print("  ✅ Row limit support")
    print("  ✅ Security validation")
    print("  ✅ Error handling")
    print("  ✅ Parameter validation")


if __name__ == "__main__":
    try:
        test_excel_tool()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
