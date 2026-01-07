"""
Base Theme System
================

Defines the core abstractions and data structures for the theme system.

Classes:
    LightingStyle: Configuration for lighting and camera settings
    ThemeConfig: Complete theme configuration including lighting styles
    BaseTheme: Abstract base class for theme implementations
    ValidationMixin: Validation utilities for theme configurations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import re


@dataclass
class LightingStyle:
    """
    Configuration for a specific lighting style within a theme.

    Attributes:
        name: Display name for the lighting style
        description: Brief description of the lighting characteristics
        lighting_instructions: Detailed instructions for prompt enhancement
        evaluation_criteria: Criteria for evaluating enhanced prompts
        color_palette: Description of the color characteristics
        camera_settings: Technical camera specifications
    """
    name: str
    description: str
    lighting_instructions: str
    evaluation_criteria: str
    color_palette: Optional[str] = None
    camera_settings: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate lighting style configuration"""
        if not self.name or not self.description:
            raise ValueError("Lighting style must have name and description")

        if len(self.lighting_instructions) < 50:
            raise ValueError("Lighting instructions must be comprehensive (50+ chars)")


@dataclass
class ThemeConfig:
    """
    Complete configuration for a photography theme.

    Attributes:
        name: Internal theme name (lowercase, underscores)
        display_name: Human-readable theme name
        description: Theme description
        theme_specific_notes: Detailed requirements for this theme
        lighting_styles: Dict of available lighting styles for this theme
        evaluation_criteria: Base evaluation criteria
        keywords: List of keywords associated with this theme
        minimum_word_count: Minimum words required in enhanced prompts
    """
    name: str
    display_name: str
    description: str
    theme_specific_notes: str
    lighting_styles: Dict[str, LightingStyle] = field(default_factory=dict)
    evaluation_criteria: Optional[Dict[str, Any]] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    minimum_word_count: int = 60

    # Advanced theme support for Edge-of-Frame and similar complex themes
    min_words: Optional[int] = None
    max_words: Optional[int] = None
    mandatory_keywords: Optional[List[List[str]]] = field(default_factory=list)
    required_elements: Optional[Dict[str, Dict[str, Any]]] = field(default_factory=dict)
    technical_requirements: Optional[Dict[str, List[str]]] = field(default_factory=dict)
    forbidden_elements: Optional[List[str]] = field(default_factory=list)
    scoring_weights: Optional[Dict[str, float]] = field(default_factory=dict)
    physics_requirements: Optional[List[str]] = field(default_factory=list)
    arrangement_types: Optional[Dict[str, Dict[str, Any]]] = field(default_factory=dict)
    authenticity_guidelines: Optional[List[str]] = field(default_factory=list)
    detail_emphasis: Optional[List[str]] = field(default_factory=list)
    specific_prompts: Optional[List[str]] = field(default_factory=list)
    example_scenarios: Optional[List[str]] = field(default_factory=list)
    realism_checklist: Optional[List[str]] = field(default_factory=list)

    def __post_init__(self):
        """Validate theme configuration"""
        if not self.name or not self.display_name:
            raise ValueError("Theme must have name and display_name")

        if not re.match(r'^[a-z_]+$', self.name):
            raise ValueError("Theme name must be lowercase with underscores only")

        if len(self.theme_specific_notes) < 100:
            raise ValueError("Theme specific notes must be comprehensive (100+ chars)")

        if not self.lighting_styles:
            raise ValueError("Theme must have at least one lighting style")

        # Validate advanced theme features
        if self.min_words and self.max_words and self.min_words > self.max_words:
            raise ValueError("min_words cannot be greater than max_words")

        if self.scoring_weights:
            total_weight = sum(self.scoring_weights.values())
            if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
                raise ValueError(f"Scoring weights must sum to 1.0, got {total_weight}")

    def get_lighting_style(self, style_name: str) -> Optional[LightingStyle]:
        """Get a specific lighting style by name"""
        return self.lighting_styles.get(style_name)

    def list_lighting_styles(self) -> List[str]:
        """Get list of available lighting style names"""
        return list(self.lighting_styles.keys())

    def get_default_lighting_style(self) -> LightingStyle:
        """Get the default lighting style for this theme"""
        if "default" in self.lighting_styles:
            return self.lighting_styles["default"]
        return next(iter(self.lighting_styles.values()))

    def is_advanced_theme(self) -> bool:
        """Check if this is an advanced theme with complex validation"""
        return bool(
            self.mandatory_keywords or
            self.required_elements or
            self.technical_requirements or
            self.scoring_weights or
            self.arrangement_types
        )

    def get_word_count_range(self) -> tuple[int, int]:
        """Get the word count range for this theme"""
        min_count = self.min_words or self.minimum_word_count
        max_count = self.max_words or 500  # Default max if not specified
        return min_count, max_count

    def get_mandatory_keywords(self) -> List[List[str]]:
        """Get mandatory keywords with logical grouping"""
        return self.mandatory_keywords or []

    def get_required_elements(self) -> Dict[str, Dict[str, Any]]:
        """Get required elements with validation rules"""
        return self.required_elements or {}

    def get_scoring_weights(self) -> Dict[str, float]:
        """Get scoring weights, with defaults if not specified"""
        if self.scoring_weights:
            return self.scoring_weights
        # Default weights for standard themes
        return {
            "word_count": 0.3,
            "mandatory_keywords": 0.4,
            "technical_accuracy": 0.3
        }


class ValidationMixin:
    """Mixin providing validation utilities for theme configurations"""

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that all required fields are present and non-empty"""
        for field_name in required_fields:
            if field_name not in data:
                raise ValueError(f"Required field '{field_name}' is missing")

            value = data[field_name]
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Required field '{field_name}' cannot be empty")

    @staticmethod
    def validate_hyperrealistic_requirements(instructions: str) -> List[str]:
        """Validate that instructions contain hyperrealistic requirements"""
        required_terms = [
            "hyperrealistic",
            "8K resolution",
            "ultra-detailed",
            "professional photography"
        ]

        missing_terms = []
        instructions_lower = instructions.lower()

        for term in required_terms:
            if term.lower() not in instructions_lower:
                missing_terms.append(term)

        return missing_terms

    @staticmethod
    def validate_word_count_range(text: str, min_words: int = 50, max_words: int = 500) -> bool:
        """Validate that text is within acceptable word count range"""
        word_count = len(text.split())
        return min_words <= word_count <= max_words

    @staticmethod
    def validate_mandatory_keywords(text: str, mandatory_groups: List[List[str]]) -> Dict[str, Any]:
        """Validate mandatory keywords with logical grouping (AND between groups, OR within groups)"""
        text_lower = text.lower()
        results = {
            "passed": True,
            "missing_groups": [],
            "found_keywords": [],
            "group_results": []
        }

        for i, keyword_group in enumerate(mandatory_groups):
            group_found = False
            found_in_group = []

            for keyword in keyword_group:
                if keyword.lower() in text_lower:
                    group_found = True
                    found_in_group.append(keyword)
                    results["found_keywords"].append(keyword)

            results["group_results"].append({
                "group_index": i,
                "found": group_found,
                "keywords_found": found_in_group,
                "keywords_required": keyword_group
            })

            if not group_found:
                results["passed"] = False
                results["missing_groups"].append(i)

        return results

    @staticmethod
    def validate_required_elements(text: str, required_elements: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate required elements with complex validation rules"""
        text_lower = text.lower()
        results = {
            "passed": True,
            "element_results": {},
            "total_score": 0.0
        }

        for element_name, element_config in required_elements.items():
            any_of = element_config.get("any_of", [])
            min_count = element_config.get("min_count", 1)

            found_count = 0
            found_items = []

            for item in any_of:
                if item.lower() in text_lower:
                    found_count += 1
                    found_items.append(item)

            element_passed = found_count >= min_count

            results["element_results"][element_name] = {
                "found_count": found_count,
                "required_count": min_count,
                "found_items": found_items,
                "available_items": any_of,
                "passed": element_passed
            }

            if not element_passed:
                results["passed"] = False

            # Score based on percentage of requirements met
            if min_count > 0:
                element_score = min(1.0, found_count / min_count)
                results["total_score"] += element_score

        # Average score across all elements
        if required_elements:
            results["total_score"] /= len(required_elements)

        return results


class BaseTheme(ABC, ValidationMixin):
    """
    Abstract base class for all theme implementations.

    Provides the interface that all themes must implement and common
    functionality for theme operations.
    """

    def __init__(self, config: ThemeConfig):
        """Initialize theme with validated configuration"""
        self.validate_config(config)
        self.config = config

    @abstractmethod
    def validate_config(self, config: ThemeConfig) -> None:
        """Validate theme-specific configuration requirements"""
        pass

    @abstractmethod
    def enhance_prompt(self, original_prompt: str, lighting_style: str = "default") -> str:
        """Enhance a prompt according to this theme's requirements"""
        pass

    @abstractmethod
    def evaluate_prompt(self, enhanced_prompt: str, lighting_style: str = "default") -> Dict[str, Any]:
        """Evaluate an enhanced prompt against this theme's criteria"""
        pass

    def get_lighting_style(self, style_name: str) -> Optional[LightingStyle]:
        """Get lighting style configuration"""
        return self.config.get_lighting_style(style_name)

    def list_lighting_styles(self) -> List[str]:
        """List available lighting styles for this theme"""
        return self.config.list_lighting_styles()

    def get_keywords(self) -> List[str]:
        """Get theme keywords for auto-detection"""
        return self.config.keywords

    def get_name(self) -> str:
        """Get theme name"""
        return self.config.name

    def get_display_name(self) -> str:
        """Get human-readable theme name"""
        return self.config.display_name

    def get_description(self) -> str:
        """Get theme description"""
        return self.config.description


class AdvancedTheme(BaseTheme):
    """
    Advanced theme implementation for complex themes.
    Handles complex validation rules, weighted scoring, and sophisticated requirements.
    """

    def validate_config(self, config: ThemeConfig) -> None:
        """Validate advanced theme configuration"""
        required_fields = ["name", "display_name", "description", "theme_specific_notes"]
        data = {
            "name": config.name,
            "display_name": config.display_name,
            "description": config.description,
            "theme_specific_notes": config.theme_specific_notes
        }
        self.validate_required_fields(data, required_fields)

        # Validate advanced features if present
        if config.mandatory_keywords:
            for group in config.mandatory_keywords:
                if not isinstance(group, list) or not group:
                    raise ValueError("Each mandatory keyword group must be a non-empty list")

        if config.required_elements:
            for element_name, element_config in config.required_elements.items():
                if "any_of" not in element_config:
                    raise ValueError(f"Required element '{element_name}' must have 'any_of' field")
                if not isinstance(element_config["any_of"], list):
                    raise ValueError(f"'any_of' for element '{element_name}' must be a list")

    def enhance_prompt(self, original_prompt: str, lighting_style: str = "default") -> str:
        """Enhance prompt with advanced theme requirements"""
        lighting = self.get_lighting_style(lighting_style)
        if not lighting:
            lighting = self.config.get_default_lighting_style()

        enhanced = original_prompt

        # Add hyperrealistic requirements if missing
        if "hyperrealistic" not in enhanced.lower():
            enhanced = f"Hyperrealistic photograph of {enhanced.lower()}"

        # Add technical requirements from technical_requirements if available
        if self.config.technical_requirements:
            tech_reqs = []
            for category, requirements in self.config.technical_requirements.items():
                if requirements:
                    tech_reqs.extend(requirements[:1])  # Add one requirement from each category

            if tech_reqs:
                enhanced += f", {', '.join(tech_reqs)}"

        # Apply lighting style instructions
        if lighting and lighting.lighting_instructions:
            # Extract key enhancement instructions
            instructions = lighting.lighting_instructions
            if "8K resolution" in instructions and "8K" not in enhanced:
                enhanced += ", 8K resolution"
            if "ultra-detailed" in instructions and "ultra-detailed" not in enhanced.lower():
                enhanced += ", ultra-detailed"

        return enhanced

    def evaluate_prompt(self, enhanced_prompt: str, lighting_style: str = "default") -> Dict[str, Any]:
        """Evaluate prompt with advanced scoring system"""
        results = {
            "overall_score": 0.0,
            "detailed_scores": {},
            "validation_results": {},
            "passed": False
        }

        # Get scoring weights
        weights = self.config.get_scoring_weights()

        # Word count validation
        min_words, max_words = self.config.get_word_count_range()
        word_count = len(enhanced_prompt.split())
        word_score = 1.0 if min_words <= word_count <= max_words else 0.0
        results["detailed_scores"]["word_count"] = word_score
        results["validation_results"]["word_count"] = {
            "actual": word_count,
            "min_required": min_words,
            "max_allowed": max_words,
            "passed": word_score == 1.0
        }

        # Mandatory keywords validation
        if self.config.mandatory_keywords:
            keyword_results = self.validate_mandatory_keywords(
                enhanced_prompt, self.config.mandatory_keywords
            )
            keyword_score = 1.0 if keyword_results["passed"] else 0.0
            results["detailed_scores"]["mandatory_keywords"] = keyword_score
            results["validation_results"]["mandatory_keywords"] = keyword_results
        else:
            results["detailed_scores"]["mandatory_keywords"] = 1.0

        # Required elements validation
        if self.config.required_elements:
            elements_results = self.validate_required_elements(
                enhanced_prompt, self.config.required_elements
            )
            elements_score = elements_results["total_score"]
            results["detailed_scores"]["required_elements"] = elements_score
            results["validation_results"]["required_elements"] = elements_results
        else:
            results["detailed_scores"]["required_elements"] = 1.0

        # Technical accuracy (basic hyperrealistic terms check)
        missing_terms = self.validate_hyperrealistic_requirements(enhanced_prompt)
        tech_score = 1.0 if not missing_terms else 0.5
        results["detailed_scores"]["technical_accuracy"] = tech_score
        results["validation_results"]["technical_accuracy"] = {
            "missing_terms": missing_terms,
            "passed": len(missing_terms) == 0
        }

        # Physical realism (basic check for forbidden elements)
        forbidden_score = 1.0
        if self.config.forbidden_elements:
            found_forbidden = []
            prompt_lower = enhanced_prompt.lower()
            for forbidden in self.config.forbidden_elements:
                if forbidden.lower() in prompt_lower:
                    found_forbidden.append(forbidden)

            forbidden_score = 0.0 if found_forbidden else 1.0
            results["validation_results"]["physical_realism"] = {
                "forbidden_found": found_forbidden,
                "passed": forbidden_score == 1.0
            }

        results["detailed_scores"]["physical_realism"] = forbidden_score

        # Calculate weighted overall score
        overall_score = 0.0
        for category, weight in weights.items():
            if category in results["detailed_scores"]:
                overall_score += results["detailed_scores"][category] * weight

        results["overall_score"] = overall_score
        results["passed"] = overall_score >= 0.7  # Require 70% to pass

        return results


class DefaultTheme(BaseTheme):
    """
    Default theme implementation for general photography prompts.
    Used as fallback when no specific theme is detected or specified.
    """

    def validate_config(self, config: ThemeConfig) -> None:
        """Validate default theme configuration"""
        required_fields = ["name", "display_name", "description", "theme_specific_notes"]
        data = {
            "name": config.name,
            "display_name": config.display_name,
            "description": config.description,
            "theme_specific_notes": config.theme_specific_notes
        }
        self.validate_required_fields(data, required_fields)

    def enhance_prompt(self, original_prompt: str, lighting_style: str = "default") -> str:
        """Enhance prompt with general hyperrealistic requirements"""
        lighting = self.get_lighting_style(lighting_style)
        if not lighting:
            lighting = self.config.get_default_lighting_style()

        # Basic enhancement following hyperrealistic requirements
        if "hyperrealistic" not in original_prompt.lower():
            enhanced = f"Hyperrealistic photograph of {original_prompt.lower()}"
        else:
            enhanced = original_prompt

        # Add technical requirements if missing
        technical_terms = ["8K resolution", "ultra-detailed", "professional photography"]
        for term in technical_terms:
            if term.lower() not in enhanced.lower():
                enhanced += f", {term}"

        return enhanced

    def evaluate_prompt(self, enhanced_prompt: str, lighting_style: str = "default") -> Dict[str, Any]:
        """Evaluate prompt against general hyperrealistic criteria"""
        word_count = len(enhanced_prompt.split())

        # Check for required hyperrealistic elements
        missing_terms = self.validate_hyperrealistic_requirements(enhanced_prompt)

        # Basic scoring
        score = "pass" if word_count >= self.config.minimum_word_count and not missing_terms else "fail"

        return {
            "score": score,
            "word_count": word_count,
            "missing_terms": missing_terms,
            "meets_length_requirement": word_count >= self.config.minimum_word_count,
            "has_hyperrealistic_elements": len(missing_terms) == 0
        }
