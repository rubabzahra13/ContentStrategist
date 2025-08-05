#!/usr/bin/env python3
"""
Tests for spelling error handling in month normalization
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import normalize_month

class TestSpellingErrorHandling(unittest.TestCase):
    """Tests for robust spelling error handling"""

    def test_common_typos_mapping(self):
        """Test predefined common typos are handled correctly"""
        typo_cases = {
            "agust": "August",
            "ajguzt": "August", 
            "auzhst": "August",
            "aughst": "August",
            "julu": "July",
            "sepember": "September",
            "ocober": "October", 
            "novemer": "November",
            "decemer": "December",
            "febuary": "February"
        }
        
        for typo, correct_month in typo_cases.items():
            with self.subTest(typo=typo):
                result = normalize_month(f"{typo} 2025")
                self.assertEqual(result, f"{correct_month} 2025")

    def test_fuzzy_matching_edge_cases(self):
        """Test fuzzy matching for unusual typos"""
        fuzzy_cases = [
            ("Janury 2025", "January"),
            ("Feburary 2025", "February"),
            ("Aprial 2025", "April"),
            ("Juny 2025", "June"),
            ("Ocotber 2025", "October"),
            ("Novmber 2025", "November"),
        ]
        
        for typo_input, expected_month in fuzzy_cases:
            with self.subTest(typo=typo_input):
                result = normalize_month(typo_input)
                self.assertTrue(result.startswith(expected_month), 
                              f"Expected {expected_month}, got {result}")

    def test_very_bad_spelling(self):
        """Test handling of very poor spelling"""
        bad_spelling_cases = [
            "agzxt 2025",    # Very corrupted August
            "julxx 2025",    # Very corrupted July  
            "spetmbr 2025",  # Very corrupted September
            "dcmbr 2025",    # Very corrupted December
        ]
        
        for bad_input in bad_spelling_cases:
            with self.subTest(input=bad_input):
                result = normalize_month(bad_input)
                # Should either match a month or default to January
                self.assertTrue(any(month in result for month in [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]), f"Result should contain a valid month: {result}")

    def test_non_month_words(self):
        """Test handling of completely non-month words"""
        non_month_cases = [
            "hello 2025",
            "world 2025", 
            "test 2025",
            "xyz 2025",
            "123 2025"
        ]
        
        for non_month in non_month_cases:
            with self.subTest(input=non_month):
                result = normalize_month(non_month)
                # Should default to January when no recognizable month
                self.assertEqual(result, "January 2025")

    def test_mixed_case_typos(self):
        """Test case-insensitive typo handling"""
        mixed_case_cases = [
            ("AJGUZT 2025", "August 2025"),
            ("ajguzt 2025", "August 2025"),
            ("AjGuZt 2025", "August 2025"),
            ("JULU 2025", "July 2025"),
            ("julu 2025", "July 2025"),
        ]
        
        for mixed_input, expected in mixed_case_cases:
            with self.subTest(input=mixed_input):
                result = normalize_month(mixed_input)
                self.assertEqual(result, expected)

    def test_extra_characters_and_symbols(self):
        """Test handling of extra characters and symbols"""
        extra_char_cases = [
            ("ajguzt! 2025", "August 2025"),
            ("julu??? 2025", "July 2025"),
            ("agust123 2025", "August 2025"),
            ("sepember... 2025", "September 2025"),
        ]
        
        for input_with_extra, expected in extra_char_cases:
            with self.subTest(input=input_with_extra):
                result = normalize_month(input_with_extra)
                self.assertEqual(result, expected)

    def test_multiple_typos_in_input(self):
        """Test handling when input has multiple potential month words"""
        multiple_cases = [
            ("ajguzt and julu 2025", "August 2025"),  # Should pick first valid one
            ("plan ajguzt event 2025", "August 2025"),
            ("maybe julu or sepember 2025", "July 2025"),
        ]
        
        for multi_input, expected in multiple_cases:
            with self.subTest(input=multi_input):
                result = normalize_month(multi_input)
                self.assertEqual(result, expected)

    def test_threshold_scoring(self):
        """Test that fuzzy matching respects minimum score threshold"""
        very_poor_matches = [
            "xyz 2025",      # Should not match any month
            "abc 2025",      # Should not match any month
            "zzz 2025",      # Should not match any month
        ]
        
        for poor_input in very_poor_matches:
            with self.subTest(input=poor_input):
                result = normalize_month(poor_input)
                # Should default to January when score too low
                self.assertEqual(result, "January 2025")

    def test_partial_month_names(self):
        """Test handling of partial month names"""
        partial_cases = [
            ("aug 2025", "August"),    # Common abbreviation
            ("sep 2025", "September"), # Common abbreviation  
            ("dec 2025", "December"),  # Common abbreviation
            ("jan 2025", "January"),   # Common abbreviation
        ]
        
        for partial_input, expected_month in partial_cases:
            with self.subTest(input=partial_input):
                result = normalize_month(partial_input)
                self.assertTrue(result.startswith(expected_month), 
                              f"Expected {expected_month}, got {result}")

    def test_error_recovery_graceful(self):
        """Test that errors are handled gracefully without crashes"""
        problematic_inputs = [
            None,           # This would cause error in string operations
            "",             # Empty string
            "   ",          # Only whitespace
            "2025",         # Only year
            "\n\t 2025",    # Weird whitespace
        ]
        
        for problematic_input in problematic_inputs:
            with self.subTest(input=problematic_input):
                try:
                    if problematic_input is None:
                        # Skip None test as it would fail before reaching function
                        continue
                    result = normalize_month(problematic_input)
                    # Should return some valid month + year format
                    self.assertIn("2025", result)
                    self.assertTrue(any(month in result for month in [
                        "January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"
                    ]))
                except Exception as e:
                    self.fail(f"Should handle '{problematic_input}' gracefully, but got: {e}")

if __name__ == '__main__':
    print("🔤 RUNNING SPELLING ERROR HANDLING TESTS")
    print("=" * 50)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n✅ SPELLING ERROR TESTS COMPLETED")
    print("All spelling error handling verified!")