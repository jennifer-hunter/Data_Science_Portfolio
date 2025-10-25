"""
Theme Loader System
==================

Provides dynamic loading, caching, and management of theme configurations.

Classes:
    ThemeRegistry: Central registry for theme loading and caching

Functions:
    load_theme: Load a specific theme by name
    list_available_themes: Get list of all available themes
    reload_theme: Force reload a theme from disk
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from functools import lru_cache
import logging

from .base_theme import BaseTheme, DefaultTheme, AdvancedTheme, ThemeConfig, LightingStyle

# Setup logging (must be before first use)
logger = logging.getLogger(__name__)

# Add database path for mixed theme support
current_dir = Path(__file__).parent
database_dir = current_dir.parent.parent / "database"
if str(database_dir) not in sys.path:
    sys.path.insert(0, str(database_dir))

# Import security utilities
try:
    from security_utils import validate_safe_path, sanitize_filename
    SECURITY_UTILS_AVAILABLE = True
except ImportError:
    logger.warning("Security utilities not available, path validation disabled")
    SECURITY_UTILS_AVAILABLE = False
    validate_safe_path = None
    sanitize_filename = None

# Import database utils for mixed theme loading
try:
    from database_utils import DatabaseManager
    MIXED_THEMES_SUPPORTED = True
except ImportError:
    print("Warning: Database support not available, mixed themes will be disabled")
    DatabaseManager = None
    MIXED_THEMES_SUPPORTED = False


class ThemeRegistry:
    """
    Central registry for theme loading, caching, and management.

    Handles:
    - Dynamic loading of theme definitions from YAML files
    - Caching of loaded themes for performance
    - Validation of theme configurations
    - Auto-discovery of available themes
    """

    def __init__(self, definitions_dir: Optional[Path] = None):
        """
        Initialize the theme registry.

        Args:
            definitions_dir: Directory containing theme YAML files.
                           If None, uses the default definitions directory.
        """
        if definitions_dir is None:
            # Default to definitions directory relative to this file
            current_dir = Path(__file__).parent
            definitions_dir = current_dir / "definitions"

        self.definitions_dir = Path(definitions_dir)
        self._theme_cache: Dict[str, BaseTheme] = {}
        self._config_cache: Dict[str, ThemeConfig] = {}

        # Initialize database manager for mixed theme support
        self.db_manager = None
        if MIXED_THEMES_SUPPORTED:
            try:
                self.db_manager = DatabaseManager()
                logger.info("Mixed theme support enabled with database connection")
            except Exception as e:
                logger.warning(f"Mixed theme support disabled, database connection failed: {e}")

        # Ensure definitions directory exists
        if not self.definitions_dir.exists():
            logger.warning(f"Theme definitions directory not found: {self.definitions_dir}")
            self.definitions_dir.mkdir(parents=True, exist_ok=True)

    def list_available_themes(self) -> List[str]:
        """
        Get list of all available theme names.

        Returns:
            List of theme names (without .yaml extension)
        """
        themes = []

        # Get regular themes from YAML files
        if self.definitions_dir.exists():
            theme_files = self.definitions_dir.glob("*.yaml")
            themes.extend([f.stem for f in theme_files if f.is_file()])

        return list(set(themes))  # Remove duplicates

    def _validate_theme_name(self, theme_name: str) -> bool:
        """
        Validate theme name to prevent path traversal attacks

        Args:
            theme_name: Theme name to validate

        Returns:
            True if valid, False if suspicious
        """
        # Theme names should only contain alphanumeric, underscore, and hyphen
        if not theme_name:
            logger.warning("Empty theme name rejected")
            return False

        # Check for path traversal attempts
        if '..' in theme_name or '/' in theme_name or '\\' in theme_name:
            logger.warning(f"[SECURITY WARNING] Path traversal attempt in theme name: {theme_name}")
            return False

        # Check for null bytes
        if '\x00' in theme_name:
            logger.warning(f"[SECURITY WARNING] Null byte in theme name: {theme_name}")
            return False

        # Reasonable length check
        if len(theme_name) > 100:
            logger.warning(f"[SECURITY WARNING] Theme name too long: {len(theme_name)} chars")
            return False

        return True

    def theme_exists(self, theme_name: str) -> bool:
        """Check if a theme definition file exists"""
        # Validate theme name first
        if not self._validate_theme_name(theme_name):
            return False

        # Check regular theme file
        theme_file = self.definitions_dir / f"{theme_name}.yaml"

        # Additional security: validate the resolved path
        if SECURITY_UTILS_AVAILABLE and validate_safe_path:
            safe_path = validate_safe_path(theme_file, self.definitions_dir)
            if not safe_path:
                logger.warning(f"[SECURITY WARNING] Theme file path rejected: {theme_file}")
                return False
            theme_file = safe_path

        return theme_file.exists()

    def load_theme_config(self, theme_name: str, use_cache: bool = True) -> ThemeConfig:
        """
        Load theme configuration from YAML file.

        Args:
            theme_name: Name of the theme to load
            use_cache: Whether to use cached configuration

        Returns:
            ThemeConfig object

        Raises:
            FileNotFoundError: If theme doesn't exist
            ValueError: If theme configuration is invalid
            yaml.YAMLError: If YAML parsing fails
        """
        # Validate theme name first (security)
        if not self._validate_theme_name(theme_name):
            raise ValueError(f"Invalid theme name: {theme_name}")

        # Check cache first
        if use_cache and theme_name in self._config_cache:
            return self._config_cache[theme_name]

        # Check if there's a YAML file
        theme_file = self.definitions_dir / f"{theme_name}.yaml"

        # Security: validate the resolved path
        if SECURITY_UTILS_AVAILABLE and validate_safe_path:
            safe_path = validate_safe_path(theme_file, self.definitions_dir)
            if not safe_path:
                raise ValueError(f"Theme file path validation failed: {theme_name}")
            theme_file = safe_path

        if theme_file.exists():
            # Load from YAML file
            with open(theme_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            config = self._parse_theme_config(config_data, theme_name)
            if use_cache:
                self._config_cache[theme_name] = config
            logger.info(f"Loaded theme configuration from YAML: {theme_name}")
            return config

        # If we get here, theme file doesn't exist
        raise FileNotFoundError(f"Theme definition not found: {theme_name}")

    def _parse_theme_config(self, yaml_data: Dict[str, Any], theme_name: str) -> ThemeConfig:
        """Parse YAML data into ThemeConfig object"""

        # Extract basic theme information
        name = yaml_data.get('name', theme_name)
        display_name = yaml_data.get('display_name', name.title())
        description = yaml_data.get('description', f"{display_name} photography theme")
        theme_specific_notes = yaml_data.get('theme_specific_notes', '')

        # Parse lighting styles
        lighting_styles = {}
        lighting_data = yaml_data.get('lighting_styles', {})

        for style_name, style_config in lighting_data.items():
            lighting_style = LightingStyle(
                name=style_config.get('name', style_name.title()),
                description=style_config.get('description', ''),
                lighting_instructions=style_config.get('instructions', style_config.get('lighting_instructions', '')),
                evaluation_criteria=style_config.get('evaluation_criteria', ''),
                color_palette=style_config.get('color_palette'),
                camera_settings=style_config.get('camera_settings', {})
            )
            lighting_styles[style_name] = lighting_style

        # If no lighting styles defined, create a default one
        if not lighting_styles:
            default_style = LightingStyle(
                name="Default Style",
                description="Standard hyperrealistic photography",
                lighting_instructions="Enhance with hyperrealistic details, 8K resolution, professional photography quality.",
                evaluation_criteria="Must include hyperrealistic elements and detailed descriptions."
            )
            lighting_styles['default'] = default_style

        # Parse other configuration
        evaluation_criteria = yaml_data.get('evaluation_criteria', {})
        keywords = yaml_data.get('keywords', [])
        minimum_word_count = yaml_data.get('minimum_word_count', 60)

        # Parse advanced theme features (for Edge-of-Frame and similar complex themes)
        min_words = yaml_data.get('min_words')
        max_words = yaml_data.get('max_words')
        mandatory_keywords = yaml_data.get('mandatory_keywords', [])
        required_elements = yaml_data.get('required_elements', {})
        technical_requirements = yaml_data.get('technical_requirements', {})
        forbidden_elements = yaml_data.get('forbidden_elements', [])
        scoring_weights = yaml_data.get('scoring_weights', {})
        physics_requirements = yaml_data.get('physics_requirements', [])
        arrangement_types = yaml_data.get('arrangement_types', {})
        authenticity_guidelines = yaml_data.get('authenticity_guidelines', [])
        detail_emphasis = yaml_data.get('detail_emphasis', [])
        specific_prompts = yaml_data.get('specific_prompts', [])
        example_scenarios = yaml_data.get('example_scenarios', [])
        realism_checklist = yaml_data.get('realism_checklist', [])

        return ThemeConfig(
            name=name,
            display_name=display_name,
            description=description,
            theme_specific_notes=theme_specific_notes,
            lighting_styles=lighting_styles,
            evaluation_criteria=evaluation_criteria,
            keywords=keywords,
            minimum_word_count=minimum_word_count,
            # Advanced features
            min_words=min_words,
            max_words=max_words,
            mandatory_keywords=mandatory_keywords,
            required_elements=required_elements,
            technical_requirements=technical_requirements,
            forbidden_elements=forbidden_elements,
            scoring_weights=scoring_weights,
            physics_requirements=physics_requirements,
            arrangement_types=arrangement_types,
            authenticity_guidelines=authenticity_guidelines,
            detail_emphasis=detail_emphasis,
            specific_prompts=specific_prompts,
            example_scenarios=example_scenarios,
            realism_checklist=realism_checklist
        )

    def load_theme(self, theme_name: str, use_cache: bool = True) -> BaseTheme:
        """
        Load a complete theme instance.

        Args:
            theme_name: Name of the theme to load
            use_cache: Whether to use cached theme instance

        Returns:
            BaseTheme instance (DefaultTheme for now, extensible for custom themes)

        Raises:
            FileNotFoundError: If theme doesn't exist
            ValueError: If theme configuration is invalid
        """
        # Check cache first
        if use_cache and theme_name in self._theme_cache:
            return self._theme_cache[theme_name]

        # Load configuration
        config = self.load_theme_config(theme_name, use_cache)

        # Create theme instance - use AdvancedTheme for complex themes
        if config.is_advanced_theme():
            theme = AdvancedTheme(config)
            logger.info(f"Created advanced theme instance for: {theme_name}")
        else:
            theme = DefaultTheme(config)
            logger.info(f"Created default theme instance for: {theme_name}")

        # Cache the theme
        if use_cache:
            self._theme_cache[theme_name] = theme

        logger.info(f"Loaded theme instance: {theme_name}")
        return theme

    def reload_theme(self, theme_name: str) -> BaseTheme:
        """
        Force reload a theme from disk, bypassing cache.

        Args:
            theme_name: Name of theme to reload

        Returns:
            Fresh BaseTheme instance
        """
        # Clear from caches
        self._theme_cache.pop(theme_name, None)
        self._config_cache.pop(theme_name, None)

        # Load fresh from disk
        return self.load_theme(theme_name, use_cache=False)

    def clear_cache(self) -> None:
        """Clear all cached themes and configurations"""
        self._theme_cache.clear()
        self._config_cache.clear()
        logger.info("Theme cache cleared")

    def validate_theme(self, theme_name: str) -> Dict[str, Any]:
        """
        Validate a theme configuration without loading it.

        Args:
            theme_name: Name of theme to validate

        Returns:
            Dict with validation results
        """
        validation_result = {
            "theme_name": theme_name,
            "valid": False,
            "errors": [],
            "warnings": []
        }

        try:
            # Try to load the configuration
            config = self.load_theme_config(theme_name, use_cache=False)

            # Basic validation passed if we got here
            validation_result["valid"] = True

            # Additional checks
            if not config.keywords:
                validation_result["warnings"].append("No keywords defined for theme detection")

            if config.minimum_word_count < 50:
                validation_result["warnings"].append("Minimum word count is quite low")

        except Exception as e:
            validation_result["errors"].append(str(e))

        return validation_result


# Global registry instance
_global_registry: Optional[ThemeRegistry] = None


def get_registry() -> ThemeRegistry:
    """Get the global theme registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ThemeRegistry()
    return _global_registry


def load_theme(theme_name: str, use_cache: bool = True) -> BaseTheme:
    """
    Load a theme by name using the global registry.

    Args:
        theme_name: Name of theme to load
        use_cache: Whether to use cached instance

    Returns:
        BaseTheme instance
    """
    return get_registry().load_theme(theme_name, use_cache)


def list_available_themes() -> List[str]:
    """
    Get list of all available theme names.

    Returns:
        List of theme names
    """
    return get_registry().list_available_themes()


def reload_theme(theme_name: str) -> BaseTheme:
    """
    Force reload a theme from disk.

    Args:
        theme_name: Name of theme to reload

    Returns:
        Fresh BaseTheme instance
    """
    return get_registry().reload_theme(theme_name)


def theme_exists(theme_name: str) -> bool:
    """
    Check if a theme exists.

    Args:
        theme_name: Name of theme to check

    Returns:
        True if theme definition file exists
    """
    return get_registry().theme_exists(theme_name)


def validate_theme(theme_name: str) -> Dict[str, Any]:
    """
    Validate a theme configuration.

    Args:
        theme_name: Name of theme to validate

    Returns:
        Dict with validation results
    """
    return get_registry().validate_theme(theme_name)


def clear_theme_cache() -> None:
    """Clear all cached themes"""
    get_registry().clear_cache()


# Backward compatibility function for the existing codebase
def get_theme_config(theme_name: str) -> Dict[str, Any]:
    """
    Get theme configuration in the original format for backward compatibility.

    Args:
        theme_name: Name of theme to get

    Returns:
        Dict in the original THEME_JUDGE_CONFIGS format
    """
    try:
        config = get_registry().load_theme_config(theme_name)

        # Convert to original format
        return {
            "theme_specific_notes": config.theme_specific_notes
        }
    except Exception as e:
        logger.warning(f"Could not load theme {theme_name}, using default: {e}")

        # Return default theme config
        return {
            "theme_specific_notes": (
                "GENERAL HYPERREALISTIC REQUIREMENTS:\n"
                "- Every surface must have described texture and material properties\n"
                "- Include environmental context and atmospheric conditions\n"
                "- Add human elements with realistic imperfections\n"
                "- Describe light behavior on different materials\n"
                "- Include age, wear, and weathering where appropriate\n"
                "- Minimum 60+ words of comprehensive photographic detail"
            )
        }


def get_lighting_config(lighting_style: str) -> Dict[str, Any]:
    """
    Get lighting configuration in original format for backward compatibility.

    Args:
        lighting_style: Name of lighting style

    Returns:
        Dict in original LIGHTING_STYLES format
    """
    # For backward compatibility, map old lighting style names to defaults
    lighting_mapping = {
        "autumn": "documentary",
        "summer": "bright_sunny",
        "hyperreal_standard": "default"
    }

    # Try to find the lighting style in any available theme
    for theme_name in list_available_themes():
        try:
            config = get_registry().load_theme_config(theme_name)

            # Check direct match first
            if lighting_style in config.lighting_styles:
                style = config.lighting_styles[lighting_style]
                return {
                    "style_name": style.name,
                    "lighting_description": style.description,
                    "lighting_instructions": style.lighting_instructions,
                    "evaluation_criteria": style.evaluation_criteria,
                    "color_palette": style.color_palette or "natural colors"
                }

            # Check mapped name
            mapped_name = lighting_mapping.get(lighting_style)
            if mapped_name and mapped_name in config.lighting_styles:
                style = config.lighting_styles[mapped_name]
                return {
                    "style_name": style.name,
                    "lighting_description": style.description,
                    "lighting_instructions": style.lighting_instructions,
                    "evaluation_criteria": style.evaluation_criteria,
                    "color_palette": style.color_palette or "natural colors"
                }
        except Exception:
            continue

    # Default fallback
    return {
        "style_name": "HYPERREALISTIC STANDARD STYLE",
        "lighting_description": "Standard hyperrealistic photography lighting",
        "lighting_instructions": "Enhance with professional photography details, 8K resolution, ultra-detailed textures.",
        "evaluation_criteria": "Must include hyperrealistic elements and comprehensive detail.",
        "color_palette": "natural, true-to-life colors"
    }


def get_backward_compatibility_themes() -> Dict[str, Any]:
    """
    Get theme configurations in the old LIGHTING_STYLES format for backward compatibility.

    Returns:
        Dict mapping theme names to old format configurations
    """
    backward_configs = {}

    # Legacy lighting style mappings
    legacy_styles = {
        "autumn": {
            "style_name": "AUTUMN HYPERREALISTIC DOCUMENTARY STYLE",
            "lighting_description": "flat overcast lighting with muted colors for photorealistic documentary photography",
            "color_palette": "muted, neutral colors with subtle earth tones",
            "lighting_instructions": (
                "ENHANCE PROMPT TO BE HYPERREALISTIC AND HIGHLY DETAILED:\n"
                "- MUST ADD: 'Hyperrealistic photograph', 'photorealistic quality', '8K resolution'\n"
                "- MUST ADD: 'Ultra-detailed textures', 'lifelike skin tones and fabric textures'\n"
                "- MUST ADD: 'Professional DSLR quality', 'RAW format', 'unprocessed authentic look'\n"
                "- MUST ADD: Extensive environmental details (weather conditions, atmospheric particles, ground textures)\n"
            ),
            "evaluation_criteria": (
                "REQUIRED HYPERREALISTIC ELEMENTS (ALL MANDATORY):\n"
                "- 'Hyperrealistic' or 'photorealistic' explicitly stated\n"
                "- Minimum 60+ words of detailed description\n"
                "- Technical photography terminology included\n"
            )
        },
        "summer": {
            "style_name": "SUMMER HYPERREALISTIC BRIGHT STYLE",
            "lighting_description": "bright even lighting with enhanced natural colors for photorealistic summer photography",
            "color_palette": "bright, enhanced but photorealistic colors with natural vibrancy",
            "lighting_instructions": (
                "ENHANCE PROMPT TO BE HYPERREALISTIC AND HIGHLY DETAILED:\n"
                "- MUST ADD: 'Hyperrealistic summer photograph', 'photorealistic rendering', '8K resolution'\n"
                "- MUST ADD: 'Crystal clear details', 'lifelike textures and colors'\n"
                "- MUST ADD: 'Professional photography', 'magazine quality', 'commercial grade'\n"
            ),
            "evaluation_criteria": (
                "REQUIRED HYPERREALISTIC ELEMENTS (ALL MANDATORY):\n"
                "- 'Hyperrealistic' or 'photorealistic' stated at least 3 times\n"
                "- Minimum 60+ words of rich description\n"
                "- Summer-specific atmospheric details included\n"
            )
        },
        "hyperreal_standard": {
            "style_name": "HYPERREALISTIC STANDARD STYLE",
            "lighting_description": "balanced natural lighting with enhanced detail for maximum photorealism",
            "color_palette": "true-to-life colors with enhanced clarity and detail",
            "lighting_instructions": (
                "ENHANCE PROMPT TO BE HYPERREALISTIC AND HIGHLY DETAILED:\n"
                "- MUST ADD: 'Hyperrealistic photograph', 'photorealistic quality', '8K resolution'\n"
                "- MUST ADD: 'Ultra-detailed rendering', 'lifelike textures and materials'\n"
                "- MUST ADD: 'Professional photography', 'commercial quality', 'studio grade'\n"
            ),
            "evaluation_criteria": (
                "REQUIRED HYPERREALISTIC ELEMENTS (ALL MANDATORY):\n"
                "- 'Hyperrealistic' or 'photorealistic' clearly stated\n"
                "- Minimum 50+ words of detailed description\n"
                "- Technical photography terminology included\n"
            )
        }
    }

    return legacy_styles
