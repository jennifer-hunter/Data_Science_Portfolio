"""
Theme System for Photo Prompt Judge
==================================

A modular theme-based architecture for photo prompt evaluation and enhancement.

This package provides:
- BaseTheme: Abstract base class for all themes
- ThemeLoader: Dynamic loading and caching of theme configurations
- Theme definitions in YAML format for easy maintenance

Usage:
    from themes import load_theme, list_available_themes
    
    theme = load_theme("wildlife")
    available = list_available_themes()
"""

from .theme_loader import (
    ThemeRegistry, 
    load_theme, 
    list_available_themes,
    get_theme_config,
    get_lighting_config,
    get_backward_compatibility_themes
)
from .base_theme import BaseTheme, LightingStyle, ThemeConfig

__all__ = [
    'BaseTheme',
    'LightingStyle', 
    'ThemeConfig',
    'ThemeRegistry',
    'load_theme',
    'list_available_themes',
    'get_theme_config',
    'get_lighting_config', 
    'get_backward_compatibility_themes'
]

__version__ = "1.0.0"