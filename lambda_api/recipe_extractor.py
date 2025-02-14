from typing import Dict, List, Optional, Any
from metadata_extractor import MetadataExtractor
import html
import re

class RecipeExtractor:
    """
    Extract and normalize recipe data from JSON-LD metadata.
    Follows schema.org Recipe schema (https://schema.org/Recipe)
    """

    RECIPE_TYPE = 'Recipe'

    def __init__(self):
        self.metadata_extractor = MetadataExtractor()

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """
        Clean text by removing HTML entities and special characters

        Args:
            text: Text to clean

        Returns:
            Cleaned text or None if input is None
        """
        if not text:
            return None

        # Decode
        text = html.unescape(text)
        # Remove any remaining unicode escapes
        text = text.encode('ascii', 'ignore').decode('ascii')
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove html characters
        text = re.sub(r'<[^>]*>', '', text)
        return text

    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract recipe data from a URL's JSON-LD metadata

        Args:
            url: The webpage URL to extract recipe from

        Returns:
            Normalized recipe data dictionary
        """
        metadata = self.metadata_extractor.extract_from_url(url)
        return self._extract_recipe_from_jsonld(metadata.get('json_ld', []), url)

    def _extract_recipe_from_jsonld(self, json_ld: List[Dict], url: str) -> Dict[str, Any]:
        """
        Extract recipe from JSON-LD data, including nested objects

        Args:
            json_ld: List of JSON-LD objects from the webpage
            url: Original URL of the recipe

        Returns:
            Normalized recipe data or empty dict if no recipe found
        """
        def find_recipe(data: Any) -> Optional[Dict]:
            """Recursively search for Recipe type in JSON-LD data"""
            if not data:
                return None

            # Check if current object is a Recipe
            if isinstance(data, dict):
                if data.get('@type') == self.RECIPE_TYPE:
                    return data
                # Search in all values
                for value in data.values():
                    recipe = find_recipe(value)
                    if recipe:
                        return recipe
            # Search in lists
            elif isinstance(data, list):
                for item in data:
                    recipe = find_recipe(item)
                    if recipe:
                        return recipe
            return None

        # Search for recipe in all JSON-LD objects
        for item in json_ld:
            recipe_data = find_recipe(item)
            if recipe_data:
                recipe = self._normalize_recipe(recipe_data)
                if not recipe.get('url'):
                    recipe['url'] = url
                return recipe

        return {}

    def _normalize_recipe(self, data: Dict) -> Dict[str, Any]:
        """
        Normalize recipe data to a consistent format

        Args:
            data: Raw JSON-LD recipe data

        Returns:
            Normalized recipe dictionary
        """
        return {
            # Basic Information
            'name': self._clean_text(data.get('name')),
            'description': self._clean_text(data.get('description')),
            'url': data.get('url'),

            # Media
            'image': self._normalize_image(data.get('image')),

            # Authorship
            'author': self._clean_text(self._extract_author(data.get('author'))),

            'recipeCategory': self._clean_text(data.get('recipeCategory')),
            'recipeCuisine': self._clean_text(data.get('recipeCuisine')),

            # Instructions and Ingredients
            'recipeIngredient': [self._clean_text(i) for i in data.get('recipeIngredient', []) if i],
            'recipeInstructions': self._normalize_instructions(data.get('recipeInstructions', [])),

            "keywords": self._normalize_keywords(data),
            # Metadata
            'source': 'recipe-extractor'
        }

    def _normalize_keywords(self, data: Dict) -> str:
        """
        Normalize keywords to a single string
        """
        keywords = []
        if data.get('name'):
            keywords.append(self._clean_text(data.get("name", "")))
        if data.get('recipeCategory'):
            keywords.append(self._clean_text(data.get("recipeCategory", "")))
        if data.get('recipeCuisine'):
            keywords.append(self._clean_text(data.get("recipeCuisine", "")))

        keywords = list(set(keywords))
        return ' '.join(keywords).strip()

    def _normalize_image(self, image: Any) -> Optional[str]:
        """
        Normalize image data to a single URL

        Args:
            image: Image data (can be string, list, or dict)

        Returns:
            Image URL or None
        """
        if isinstance(image, str):
            return image
        elif isinstance(image, list) and image:
            return image[0] if isinstance(image[0], str) else image[0].get('url')
        elif isinstance(image, dict):
            return image.get('url')
        return None

    def _normalize_instructions(self, instructions: List[Any]) -> List[str]:
        """
        Normalize recipe instructions to a list of strings

        Args:
            instructions: List of instruction steps (can be strings or HowToStep objects)

        Returns:
            List of instruction strings
        """
        normalized = []
        for instruction in instructions:
            if isinstance(instruction, str):
                cleaned = self._clean_text(instruction)
                if cleaned:
                    normalized.append(cleaned)
            elif isinstance(instruction, dict):
                text = instruction.get('text', instruction.get('name', ''))
                cleaned = self._clean_text(text)
                if cleaned:
                    normalized.append(cleaned)
        return normalized

    def _extract_author(self, author: Any) -> Optional[str]:
        """
        Extract author information

        Args:
            author: Author data (can be string, dict, or Person object)

        Returns:
            Author name or None
        """
        if isinstance(author, str):
            return author
        elif isinstance(author, dict):
            return author.get('name')
        return None
