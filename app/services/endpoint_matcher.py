"""Endpoint matching utility for selective logging."""

import re
from typing import List

from app.config.settings import settings


class EndpointMatcher:
    """Utility class for matching endpoints against configured patterns."""
    
    def __init__(self):
        self.log_endpoints = settings.log_endpoints
        self.log_methods = [method.upper() for method in settings.log_methods]
        self.match_type = settings.endpoint_match_type.lower()
        
        # Pre-compile regex patterns if using regex matching
        if self.match_type == "regex":
            self.compiled_patterns = [
                re.compile(pattern) for pattern in self.log_endpoints
            ]
    
    def should_log_request(self, method: str, path: str) -> bool:
        """
        Determine if a request should be logged based on method and path.
        
        Args:
            method: HTTP method (e.g., 'POST', 'GET')
            path: Request path (e.g., '/search/indexsearch')
            
        Returns:
            True if request should be logged, False otherwise
        """
        # First check if method is in allowed methods
        if method.upper() not in self.log_methods:
            return False
        
        # Then check if path matches any configured endpoints
        return self._matches_endpoint(path)
    
    def _matches_endpoint(self, path: str) -> bool:
        """
        Check if path matches any configured endpoint pattern.
        
        Args:
            path: Request path to check
            
        Returns:
            True if path matches, False otherwise
        """
        if self.match_type == "exact":
            return path in self.log_endpoints
        
        elif self.match_type == "prefix":
            return any(path.startswith(endpoint) for endpoint in self.log_endpoints)
        
        elif self.match_type == "regex":
            return any(pattern.match(path) for pattern in self.compiled_patterns)
        
        else:
            # Default to exact matching if unknown match type
            return path in self.log_endpoints
    
    def get_matching_info(self) -> dict:
        """
        Get information about current matching configuration.
        
        Returns:
            Dictionary with matching configuration details
        """
        return {
            "endpoints": self.log_endpoints,
            "methods": self.log_methods,
            "match_type": self.match_type,
            "total_patterns": len(self.log_endpoints)
        }