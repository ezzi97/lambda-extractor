import extruct
from w3lib.html import get_base_url
import requests
from typing import Dict, List, Optional

TIMEOUT = 3

default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

pool_of_headers = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    },
    {
        "User-Agent": "Pinterestbot",
    },
    {
        "User-Agent": "APIs-Google (+https://developers.google.com/webmasters/APIs-Google.html)",
    },
    {
        "User-Agent": "DuckDuckBot",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    },

]

class MetadataExtractor:
    """
    A class to extract and normalize metadata from web pages using extruct.
    Supports JSON-LD, Open Graph, RDFa, and Microdata formats.
    """
    
    def __init__(self):
        self.syntaxes = ['json-ld', 'opengraph', 'rdfa', 'microdata']
    
    def extract_from_url(self, url: str) -> Dict[str, List]:
        """
        Extract metadata from a URL.
        
        Args:
            url: The webpage URL to extract metadata from
            
        Returns:
            Dictionary containing normalized metadata from different formats
        """
        for header in pool_of_headers:
            header_to_use = {**default_headers, **header}
            print(f"Extracting metadata from {url} with header: {header_to_use}")
            try:
                return self.extract_with_headers(url, header_to_use)
            except Exception as e:
                print(f"Error extracting metadata from {url}: {e}")
                continue
        return {}
    
    def extract_with_headers(self, url: str, headers: Optional[Dict] = None) -> Dict[str, List]:
        """
        Extract metadata from a URL with custom headers.
        
        Args:
            url: The webpage URL to extract metadata from
            headers: Optional request headers
            
        Returns:
            Dictionary containing normalized metadata from different formats
        """
        # Merge default headers with provided headers
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        base_url = get_base_url(response.text, response.url)
        print("Base URL:", base_url)
        # Extract metadata
        data = self.extract_from_html(response.text, base_url)
        return data

    def extract_from_html(self, html: str, base_url: Optional[str] = None) -> Dict[str, List]:
        """
        Extract metadata from HTML content.
        
        Args:
            html: HTML content to extract metadata from
            base_url: Optional base URL for resolving relative URLs
            
        Returns:
            Dictionary containing normalized metadata from different formats
        """
        # Extract all metadata formats with uniform structure
        data = extruct.extract(
            html,
            base_url=base_url,
            syntaxes=self.syntaxes,
            uniform=True
        )
        # Return normalized data
        return {
            'json_ld': self._normalize_jsonld(data.get('json-ld', [])),
            'opengraph': self._normalize_opengraph(data.get('opengraph', [])),
            'rdfa': self._normalize_rdfa(data.get('rdfa', [])),
            'microdata': self._normalize_microdata(data.get('microdata', []))
        }
    
    def _normalize_jsonld(self, data: List) -> List:
        """Normalize JSON-LD data - already normalized by extruct"""
        return data
    
    def _normalize_opengraph(self, data: List) -> List:
        """
        Normalize Open Graph data to a consistent format
        """
        normalized = []
        for item in data:
            if not item:
                continue
                
            normalized_item = {
                '@context': item.get('@context', {}),
                '@type': item.get('@type'),
            }
            
            # Add all other properties
            for key, value in item.items():
                if key not in ['@context', '@type']:
                    normalized_item[key] = value
                    
            normalized.append(normalized_item)
            
        return normalized
    
    def _normalize_rdfa(self, data: List) -> List:
        """
        Normalize RDFa data to a consistent format
        """
        normalized = []
        for item in data:
            if not item:
                continue
                
            normalized_item = {
                '@id': item.get('@id'),
            }
            
            # Add all other properties
            for key, value in item.items():
                if key != '@id':
                    normalized_item[key] = value
                    
            normalized.append(normalized_item)
            
        return normalized
    
    def _normalize_microdata(self, data: List) -> List:
        """
        Normalize Microdata to a consistent format
        """
        normalized = []
        for item in data:
            if not item:
                continue
                
            normalized_item = {
                '@type': item.get('type'),
                '@properties': item.get('properties', {})
            }
            normalized.append(normalized_item)
            
        return normalized 