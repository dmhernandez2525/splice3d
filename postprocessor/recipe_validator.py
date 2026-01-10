"""
Recipe Validator for Splice3D

Validates splice recipes before sending to machine.
Catches configuration errors before they cause hardware issues.
"""

from dataclasses import dataclass
from typing import Optional
import json


@dataclass
class ValidationResult:
    """Result of recipe validation."""
    valid: bool
    errors: list[str]
    warnings: list[str]
    
    def __str__(self):
        lines = []
        if self.valid:
            lines.append("✓ Recipe valid")
        else:
            lines.append("✗ Recipe invalid")
        
        for error in self.errors:
            lines.append(f"  ERROR: {error}")
        for warning in self.warnings:
            lines.append(f"  WARNING: {warning}")
        
        return "\n".join(lines)


class RecipeValidator:
    """Validates splice recipes for common issues."""
    
    # Validation thresholds
    MIN_SEGMENT_LENGTH_MM = 3.0      # Segments shorter than this may fail
    MAX_SEGMENT_LENGTH_MM = 50000.0  # 50 meters max per segment
    MAX_SEGMENTS = 10000             # Memory limit on firmware
    MAX_COLORS = 8                   # Maximum supported colors
    MIN_TOTAL_LENGTH_MM = 50.0       # Minimum useful print
    
    def validate(self, recipe: dict) -> ValidationResult:
        """
        Validate a recipe dictionary.
        
        Args:
            recipe: Parsed JSON recipe
            
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        
        # Required fields
        if "segments" not in recipe:
            errors.append("Missing 'segments' field")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        segments = recipe.get("segments", [])
        
        # Segment count
        if len(segments) == 0:
            errors.append("No segments in recipe")
        elif len(segments) > self.MAX_SEGMENTS:
            errors.append(f"Too many segments: {len(segments)} (max {self.MAX_SEGMENTS})")
        
        # Validate each segment
        total_length = 0.0
        colors_used = set()
        very_short_count = 0
        
        for i, segment in enumerate(segments):
            # Required fields
            if "length_mm" not in segment:
                errors.append(f"Segment {i}: missing 'length_mm'")
                continue
            if "color" not in segment:
                errors.append(f"Segment {i}: missing 'color'")
                continue
            
            length = segment["length_mm"]
            color = segment["color"]
            
            # Length validation
            if length <= 0:
                errors.append(f"Segment {i}: invalid length {length}")
            elif length < self.MIN_SEGMENT_LENGTH_MM:
                very_short_count += 1
            elif length > self.MAX_SEGMENT_LENGTH_MM:
                errors.append(f"Segment {i}: length {length}mm exceeds max")
            
            total_length += length
            colors_used.add(color)
        
        # Color count
        if len(colors_used) > self.MAX_COLORS:
            errors.append(f"Too many colors: {len(colors_used)} (max {self.MAX_COLORS})")
        elif len(colors_used) < 2:
            warnings.append("Only one color used - no splicing needed")
        
        # Very short segments warning
        if very_short_count > 0:
            warnings.append(
                f"{very_short_count} segments shorter than {self.MIN_SEGMENT_LENGTH_MM}mm - "
                "consider increasing min_segment_length"
            )
        
        # Total length
        if total_length < self.MIN_TOTAL_LENGTH_MM:
            warnings.append(f"Very short total length: {total_length:.1f}mm")
        
        # Metadata validation (optional)
        if "version" not in recipe:
            warnings.append("Missing 'version' field")
        
        # Estimate time
        estimated_time_hours = len(segments) * 45 / 3600  # 45s per splice
        if estimated_time_hours > 24:
            warnings.append(f"Long splice time: ~{estimated_time_hours:.1f} hours")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_file(self, filepath: str) -> ValidationResult:
        """
        Validate a recipe JSON file.
        
        Args:
            filepath: Path to recipe file
            
        Returns:
            ValidationResult
        """
        try:
            with open(filepath, 'r') as f:
                recipe = json.load(f)
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                errors=[f"Invalid JSON: {e}"],
                warnings=[]
            )
        except IOError as e:
            return ValidationResult(
                valid=False,
                errors=[f"Could not read file: {e}"],
                warnings=[]
            )
        
        return self.validate(recipe)


def validate_recipe(recipe_path: str) -> bool:
    """
    Convenience function to validate a recipe file.
    
    Args:
        recipe_path: Path to recipe JSON
        
    Returns:
        True if valid, False otherwise
    """
    validator = RecipeValidator()
    result = validator.validate_file(recipe_path)
    print(result)
    return result.valid


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python recipe_validator.py <recipe.json>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    validator = RecipeValidator()
    result = validator.validate_file(filepath)
    
    print(result)
    sys.exit(0 if result.valid else 1)
