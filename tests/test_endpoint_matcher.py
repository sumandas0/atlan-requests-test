"""Tests for endpoint matcher service."""

import pytest
from unittest.mock import patch

from app.services.endpoint_matcher import EndpointMatcher


@patch('app.services.endpoint_matcher.settings')
def test_exact_matching(mock_settings):
    """Test exact endpoint matching."""
    mock_settings.log_endpoints = ["/search/indexsearch", "/entity/lineage"]
    mock_settings.log_methods = ["POST"]
    mock_settings.endpoint_match_type = "exact"
    
    matcher = EndpointMatcher()
    
    # Should match configured endpoints
    assert matcher.should_log_request("POST", "/search/indexsearch") is True
    assert matcher.should_log_request("POST", "/entity/lineage") is True
    
    # Should not match wrong method
    assert matcher.should_log_request("GET", "/search/indexsearch") is False
    assert matcher.should_log_request("GET", "/entity/lineage") is False
    
    # Should not match wrong endpoint
    assert matcher.should_log_request("POST", "/other/endpoint") is False
    assert matcher.should_log_request("POST", "/search/different") is False


@patch('app.services.endpoint_matcher.settings')
def test_prefix_matching(mock_settings):
    """Test prefix endpoint matching."""
    mock_settings.log_endpoints = ["/api/", "/search/"]
    mock_settings.log_methods = ["POST", "PUT"]
    mock_settings.endpoint_match_type = "prefix"
    
    matcher = EndpointMatcher()
    
    # Should match endpoints with configured prefixes
    assert matcher.should_log_request("POST", "/api/users") is True
    assert matcher.should_log_request("PUT", "/api/users/123") is True
    assert matcher.should_log_request("POST", "/search/indexsearch") is True
    assert matcher.should_log_request("POST", "/search/query") is True
    
    # Should not match wrong method
    assert matcher.should_log_request("GET", "/api/users") is False
    assert matcher.should_log_request("DELETE", "/search/query") is False
    
    # Should not match wrong prefix
    assert matcher.should_log_request("POST", "/other/endpoint") is False
    assert matcher.should_log_request("POST", "/entity/lineage") is False


@patch('app.services.endpoint_matcher.settings')
def test_regex_matching(mock_settings):
    """Test regex endpoint matching."""
    mock_settings.log_endpoints = [r"/search/.*", r"/entity/(lineage|metadata)"]
    mock_settings.log_methods = ["POST"]
    mock_settings.endpoint_match_type = "regex"
    
    matcher = EndpointMatcher()
    
    # Should match regex patterns
    assert matcher.should_log_request("POST", "/search/indexsearch") is True
    assert matcher.should_log_request("POST", "/search/query") is True
    assert matcher.should_log_request("POST", "/search/anything") is True
    assert matcher.should_log_request("POST", "/entity/lineage") is True
    assert matcher.should_log_request("POST", "/entity/metadata") is True
    
    # Should not match wrong method
    assert matcher.should_log_request("GET", "/search/indexsearch") is False
    
    # Should not match non-matching patterns
    assert matcher.should_log_request("POST", "/entity/other") is False
    assert matcher.should_log_request("POST", "/other/endpoint") is False


@patch('app.services.endpoint_matcher.settings')
def test_case_insensitive_methods(mock_settings):
    """Test that HTTP methods are case insensitive."""
    mock_settings.log_endpoints = ["/test"]
    mock_settings.log_methods = ["post", "PUT"]  # lowercase
    mock_settings.endpoint_match_type = "exact"
    
    matcher = EndpointMatcher()
    
    # Should work with different cases
    assert matcher.should_log_request("POST", "/test") is True
    assert matcher.should_log_request("post", "/test") is True
    assert matcher.should_log_request("Put", "/test") is True
    assert matcher.should_log_request("PUT", "/test") is True


@patch('app.services.endpoint_matcher.settings')
def test_get_matching_info(mock_settings):
    """Test getting matching configuration info."""
    mock_settings.log_endpoints = ["/search/indexsearch", "/entity/lineage"]
    mock_settings.log_methods = ["POST", "PUT"]
    mock_settings.endpoint_match_type = "exact"
    
    matcher = EndpointMatcher()
    info = matcher.get_matching_info()
    
    assert info["endpoints"] == ["/search/indexsearch", "/entity/lineage"]
    assert info["methods"] == ["POST", "PUT"]
    assert info["match_type"] == "exact"
    assert info["total_patterns"] == 2


@patch('app.services.endpoint_matcher.settings')
def test_unknown_match_type_defaults_to_exact(mock_settings):
    """Test that unknown match type defaults to exact matching."""
    mock_settings.log_endpoints = ["/test"]
    mock_settings.log_methods = ["POST"]
    mock_settings.endpoint_match_type = "unknown"
    
    matcher = EndpointMatcher()
    
    # Should default to exact matching
    assert matcher.should_log_request("POST", "/test") is True
    assert matcher.should_log_request("POST", "/test/other") is False