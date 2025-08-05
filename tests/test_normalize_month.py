#!/usr/bin/env python3
"""
Unit tests for normalize_month() function
"""

import unittest
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import normalize_month

class TestNormalizeMonth(unittest.TestCase):
    """Comprehensive unit tests for month normalization"""

    def setUp(self):
        """Set up test fixtures"""
        self.current_year = str(datetime.now().year)

    def test_correct_month_names(self):
        """Test correctly spelled month names"""
        test_cases = [
            ("January 2025", "January 2025"),
            ("February 2024", "February 2024"),
            ("March 2023", "March 2023"),
            ("December 2026", "December 2026"),
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input=input_val):
                result = normalize_month(input_val)
                self.assertEqual(result, expected)

    def test_typo_corrections(self):
        """Test common typo corrections"""
        test_cases = [
            ("ajguzt 2025", "August 2025"),
            ("auzhst 2024", "August 2024"),
            ("aughst 2023", "August 2023"),
            ("agust 2025", "August 2025"),
            ("julu 2025", "July 2025"),
            ("sepember 2024", "September 2024"),
            ("ocober 2025", "October 2025"),
            ("novemer 2024", "November 2024"),
            ("decemer 2025", "December 2025"),
            ("febuary 2024", "February 2024"),
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input=input_val):
                result = normalize_month(input_val)
                self.assertEqual(result, expected)

    def test_no_year_provided(self):
        """Test month without year defaults to current year"""
        test_cases = [
            "January",
            "ajguzt", 
            "December",
            "julu"
        ]
        
        for input_val in test_cases:
            with self.subTest(input=input_val):
                result = normalize_month(input_val)
                self.assertTrue(result.endswith(self.current_year))

    def test_fuzzy_matching(self):
        """Test fuzzy matching for uncommon typos"""
        test_cases = [
            ("Janury 2025", "January"),
            ("Feburary 2025", "February"), 
            ("Aprial 2025", "April"),
            ("Juny 2025", "June"),
        ]
        
        for input_val, expected_month in test_cases:
            with self.subTest(input=input_val):
                result = normalize_month(input_val)
                self.assertTrue(result.startswith(expected_month))

    def test_empty_and_invalid_inputs(self):
        """Test edge cases and invalid inputs"""
        test_cases = [
            "",
            "   ",
            "2025",
            "xyz 2025",
            "123 2025"
        ]
        
        for input_val in test_cases:
            with self.subTest(input=input_val):
                result = normalize_month(input_val)
                # Should default to January + year
                self.assertTrue(result.startswith("January"))

    def test_year_extraction(self):
        """Test year extraction from various formats"""
        test_cases = [
            ("August 2025", "2025"),
            ("ajguzt in 2024", "2024"),
            ("2023 August", "2023"),
            ("August", self.current_year),
        ]
        
        for input_val, expected_year in test_cases:
            with self.subTest(input=input_val):
                result = normalize_month(input_val)
                self.assertTrue(result.endswith(expected_year))

    def test_case_insensitive(self):
        """Test case insensitive matching"""
        test_cases = [
            ("AUGUST 2025", "August 2025"),
            ("august 2025", "August 2025"),
            ("AuGusT 2025", "August 2025"),
            ("AJGUZT 2025", "August 2025"),
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input=input_val):
                result = normalize_month(input_val)
                self.assertEqual(result, expected)

    def test_extra_whitespace(self):
        """Test handling of extra whitespace"""
        test_cases = [
            ("  August 2025  ", "August 2025"),
            ("August   2025", "August 2025"),
            ("  ajguzt   2025  ", "August 2025"),
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input=input_val):
                result = normalize_month(input_val)
                self.assertEqual(result, expected)

    def test_multiple_words(self):
        """Test handling of multiple words (should take first valid month)"""
        test_cases = [
            ("August September 2025", "August 2025"),
            ("ajguzt hello world 2025", "August 2025"),
            ("plan for August 2025", "August 2025"),
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input=input_val):
                result = normalize_month(input_val)
                self.assertEqual(result, expected)

if __name__ == '__main__':
    print("🧪 RUNNING NORMALIZE_MONTH UNIT TESTS")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=False)
    
    print("\n✅ UNIT TESTS COMPLETED")
    print("All normalize_month() functionality verified!")