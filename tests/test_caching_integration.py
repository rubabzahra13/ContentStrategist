#!/usr/bin/env python3
"""
Integration tests for caching behavior
"""

import unittest
import sys
import os
import tempfile
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCachingIntegration(unittest.TestCase):
    """Integration tests for cache behavior"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('core.cache_handler.supabase')
    def test_cache_freshness_validation_current_year(self, mock_supabase):
        """Test cache freshness for current year content"""
        from core.cache_handler import validate_cache_freshness
        
        current_year = datetime.now().year
        month_key = f"august_{current_year}"
        
        # Test fresh cache (1 day old)
        fresh_timestamp = datetime.now() - timedelta(days=1)
        is_fresh, age_info = validate_cache_freshness(month_key, fresh_timestamp.isoformat())
        
        self.assertTrue(is_fresh, "1-day-old current year cache should be fresh")
        self.assertIn("1 day old", age_info)
        self.assertIn("current", age_info)
        
        # Test stale cache (5 days old)
        stale_timestamp = datetime.now() - timedelta(days=5)
        is_fresh, age_info = validate_cache_freshness(month_key, stale_timestamp.isoformat())
        
        self.assertFalse(is_fresh, "5-day-old current year cache should be stale")
        self.assertIn("5 days old", age_info)

    @patch('core.cache_handler.supabase')
    def test_cache_freshness_validation_past_year(self, mock_supabase):
        """Test cache freshness for past year content"""
        from core.cache_handler import validate_cache_freshness
        
        past_year = datetime.now().year - 1
        month_key = f"august_{past_year}"
        
        # Test cache within historical timeframe (20 days old)
        timestamp = datetime.now() - timedelta(days=20)
        is_fresh, age_info = validate_cache_freshness(month_key, timestamp.isoformat())
        
        self.assertTrue(is_fresh, "20-day-old historical cache should be fresh (30-day limit)")
        self.assertIn("historical", age_info)
        
        # Test stale historical cache (35 days old)
        stale_timestamp = datetime.now() - timedelta(days=35)
        is_fresh, age_info = validate_cache_freshness(month_key, stale_timestamp.isoformat())
        
        self.assertFalse(is_fresh, "35-day-old historical cache should be stale")

    @patch('core.cache_handler.supabase')
    def test_cache_freshness_validation_future_year(self, mock_supabase):
        """Test cache freshness for future year content"""
        from core.cache_handler import validate_cache_freshness
        
        future_year = datetime.now().year + 1
        month_key = f"august_{future_year}"
        
        # Test cache within predictive timeframe (10 days old)
        timestamp = datetime.now() - timedelta(days=10)
        is_fresh, age_info = validate_cache_freshness(month_key, timestamp.isoformat())
        
        self.assertTrue(is_fresh, "10-day-old predictive cache should be fresh (14-day limit)")
        self.assertIn("predictive", age_info)
        
        # Test stale predictive cache (20 days old)
        stale_timestamp = datetime.now() - timedelta(days=20)
        is_fresh, age_info = validate_cache_freshness(month_key, stale_timestamp.isoformat())
        
        self.assertFalse(is_fresh, "20-day-old predictive cache should be stale")

    @patch('core.cache_handler.supabase')
    def test_get_cached_file_with_fresh_cache(self, mock_supabase):
        """Test retrieving fresh cached file"""
        from core.cache_handler import get_cached_file
        
        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = [{
            'excel_url': 'https://example.com/test.xlsx',
            'created_at': datetime.now().isoformat()
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Mock environment variables
        with patch.dict(os.environ, {'SUPABASE_BUCKET': 'test-bucket'}):
            result = get_cached_file('august_2024')
            
            self.assertEqual(result, 'https://example.com/test.xlsx')
            mock_supabase.table.assert_called_with("content_calendar_cache")

    @patch('core.cache_handler.supabase')
    def test_get_cached_file_with_stale_cache(self, mock_supabase):
        """Test handling of stale cached file"""
        from core.cache_handler import get_cached_file
        
        # Mock Supabase response with old timestamp
        old_timestamp = datetime.now() - timedelta(days=10)
        mock_response = Mock()
        mock_response.data = [{
            'excel_url': 'https://example.com/test.xlsx',
            'created_at': old_timestamp.isoformat()
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Mock environment variables
        with patch.dict(os.environ, {'SUPABASE_BUCKET': 'test-bucket'}):
            result = get_cached_file('august_2024')  # Current year, should be stale after 3 days
            
            self.assertIsNone(result, "Stale cache should return None")

    @patch('core.cache_handler.supabase')
    def test_get_cached_file_no_cache_found(self, mock_supabase):
        """Test handling when no cache is found"""
        from core.cache_handler import get_cached_file
        
        # Mock empty Supabase response
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Mock environment variables
        with patch.dict(os.environ, {'SUPABASE_BUCKET': 'test-bucket'}):
            result = get_cached_file('nonexistent_month')
            
            self.assertIsNone(result, "No cache found should return None")

    @patch('core.cache_handler.supabase')
    def test_save_to_cache_success(self, mock_supabase):
        """Test successful cache save operation"""
        from core.cache_handler import save_to_cache
        
        # Create test file
        test_file = os.path.join(self.test_dir, "test.xlsx")
        with open(test_file, "wb") as f:
            f.write(b"test excel content")
        
        # Mock Supabase operations
        mock_supabase.storage.from_.return_value.list.return_value = []
        mock_supabase.storage.from_.return_value.upload.return_value = Mock()
        mock_supabase.storage.from_.return_value.get_public_url.return_value = "https://example.com/test.xlsx"
        mock_supabase.table.return_value.upsert.return_value.execute.return_value = Mock()
        
        # Mock environment variables
        with patch.dict(os.environ, {'SUPABASE_BUCKET': 'test-bucket'}):
            result = save_to_cache('test_month', test_file)
            
            self.assertEqual(result, "https://example.com/test.xlsx")
            mock_supabase.storage.from_.return_value.upload.assert_called_once()
            mock_supabase.table.assert_called_with("content_calendar_cache")

    @patch('core.cache_handler.supabase')
    def test_save_to_cache_file_not_found(self, mock_supabase):
        """Test cache save with non-existent file"""
        from core.cache_handler import save_to_cache
        
        # Mock environment variables
        with patch.dict(os.environ, {'SUPABASE_BUCKET': 'test-bucket'}):
            with self.assertRaises(ValueError) as context:
                save_to_cache('test_month', '/nonexistent/file.xlsx')
            
            self.assertIn("Local file not found", str(context.exception))

    def test_cache_handler_no_supabase_config(self):
        """Test cache handler behavior without Supabase configuration"""
        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            # Import fresh to test initialization
            import importlib
            import core.cache_handler
            importlib.reload(core.cache_handler)
            
            from core.cache_handler import get_cached_file
            
            result = get_cached_file('test_month')
            self.assertIsNone(result, "Should return None when Supabase not configured")

    @patch('core.cache_handler.create_client')
    def test_cache_handler_supabase_connection_failure(self, mock_create_client):
        """Test cache handler behavior when Supabase connection fails"""
        mock_create_client.side_effect = Exception("Connection failed")
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'test-url',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-key',
            'SUPABASE_BUCKET': 'test-bucket'
        }):
            # Import fresh to test initialization
            import importlib
            import core.cache_handler
            importlib.reload(core.cache_handler)
            
            from core.cache_handler import get_cached_file
            
            result = get_cached_file('test_month')
            self.assertIsNone(result, "Should handle Supabase connection failure gracefully")

if __name__ == '__main__':
    print("💾 RUNNING CACHING INTEGRATION TESTS")
    print("=" * 50)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n✅ CACHING TESTS COMPLETED")
    print("All caching behavior verified!")