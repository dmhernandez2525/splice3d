"""
Recipe Generator for Splice3D

Generates splice recipe JSON from parsed G-code data.
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional

from gcode_parser import ParseResult, Segment


@dataclass
class SpliceRecipe:
    """Complete splice recipe for the machine."""
    version: str = "1.0"
    total_length_mm: float = 0.0
    segment_count: int = 0
    color_count: int = 0
    segments: list[dict] = None
    colors: dict[str, str] = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.segments is None:
            self.segments = []
        if self.colors is None:
            self.colors = {}
        if self.metadata is None:
            self.metadata = {}


class RecipeGenerator:
    """
    Generates splice recipes from parsed G-code.
    """
    
    # Default color names for tool indices
    DEFAULT_COLORS = {
        0: "white",
        1: "black",
        2: "red",
        3: "blue",
        4: "green",
        5: "yellow",
        6: "orange",
        7: "purple"
    }
    
    def __init__(self, 
                 color_names: Optional[dict[int, str]] = None,
                 transition_length_mm: float = 0.0,
                 min_segment_length_mm: float = 10.0):
        """
        Initialize the recipe generator.
        
        Args:
            color_names: Custom color names for tool indices
            transition_length_mm: Extra length to add at each transition for purging
            min_segment_length_mm: Minimum segment length (smaller segments are merged)
        """
        self.color_names = color_names or self.DEFAULT_COLORS
        self.transition_length_mm = transition_length_mm
        self.min_segment_length_mm = min_segment_length_mm
    
    def generate(self, parse_result: ParseResult, source_file: str = "") -> SpliceRecipe:
        """
        Generate a splice recipe from parsed G-code.
        
        Args:
            parse_result: Result from GCodeParser
            source_file: Original G-code filename (for metadata)
            
        Returns:
            SpliceRecipe ready for serialization
        """
        # Merge small segments if needed
        merged_segments = self._merge_small_segments(parse_result.segments)
        
        # Add transition lengths
        adjusted_segments = self._add_transitions(merged_segments)
        
        # Build color map
        used_colors = set(s.color_index for s in adjusted_segments)
        colors = {str(i): self.color_names.get(i, f"color_{i}") for i in used_colors}
        
        # Convert segments to simple dicts
        segment_dicts = [
            {
                "color": s.color_index,
                "length_mm": s.length_mm
            }
            for s in adjusted_segments
        ]
        
        # Calculate total
        total_length = sum(s["length_mm"] for s in segment_dicts)
        
        return SpliceRecipe(
            version="1.0",
            total_length_mm=round(total_length, 2),
            segment_count=len(segment_dicts),
            color_count=len(colors),
            segments=segment_dicts,
            colors=colors,
            metadata={
                "source_file": source_file,
                "transition_length_mm": self.transition_length_mm,
                "original_segments": len(parse_result.segments),
                "merged_segments": len(parse_result.segments) - len(adjusted_segments)
            }
        )
    
    def _merge_small_segments(self, segments: list[Segment]) -> list[Segment]:
        """
        Merge segments smaller than min_segment_length into adjacent segments.
        
        Very small segments can cause mechanical issues and are often just
        tiny details that won't be visible anyway.
        """
        if not segments or self.min_segment_length_mm <= 0:
            return segments
        
        merged = []
        pending: Optional[Segment] = None
        
        for segment in segments:
            if pending is None:
                pending = Segment(
                    color_index=segment.color_index,
                    length_mm=segment.length_mm,
                    start_line=segment.start_line,
                    end_line=segment.end_line,
                    layer_start=segment.layer_start,
                    layer_end=segment.layer_end
                )
            elif segment.color_index == pending.color_index:
                # Same color - merge
                pending.length_mm += segment.length_mm
                pending.end_line = segment.end_line
                pending.layer_end = segment.layer_end
            elif segment.length_mm < self.min_segment_length_mm:
                # Too small - add to pending (previous color)
                pending.length_mm += segment.length_mm
                pending.end_line = segment.end_line
                pending.layer_end = segment.layer_end
            else:
                # Different color and big enough - save pending, start new
                if pending.length_mm >= self.min_segment_length_mm:
                    merged.append(pending)
                else:
                    # Pending was too small, would be lost - add to next instead
                    segment = Segment(
                        color_index=segment.color_index,
                        length_mm=segment.length_mm + pending.length_mm,
                        start_line=pending.start_line,
                        end_line=segment.end_line,
                        layer_start=pending.layer_start,
                        layer_end=segment.layer_end
                    )
                pending = segment
        
        # Don't forget the last segment
        if pending is not None:
            merged.append(pending)
        
        return merged
    
    def _add_transitions(self, segments: list[Segment]) -> list[Segment]:
        """Add transition length to segments for color purging."""
        if self.transition_length_mm <= 0:
            return segments
        
        adjusted = []
        for i, segment in enumerate(segments):
            new_length = segment.length_mm
            
            # Add transition length at the end of each segment (except last)
            if i < len(segments) - 1:
                new_length += self.transition_length_mm
            
            adjusted.append(Segment(
                color_index=segment.color_index,
                length_mm=round(new_length, 2),
                start_line=segment.start_line,
                end_line=segment.end_line,
                layer_start=segment.layer_start,
                layer_end=segment.layer_end
            ))
        
        return adjusted
    
    def to_json(self, recipe: SpliceRecipe, pretty: bool = True) -> str:
        """
        Serialize recipe to JSON string.
        
        Args:
            recipe: SpliceRecipe to serialize
            pretty: Whether to format with indentation
            
        Returns:
            JSON string
        """
        data = asdict(recipe)
        if pretty:
            return json.dumps(data, indent=2)
        return json.dumps(data)
    
    def save_recipe(self, recipe: SpliceRecipe, filepath: str):
        """
        Save recipe to a JSON file.
        
        Args:
            recipe: SpliceRecipe to save
            filepath: Output file path
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json(recipe))


def generate_recipe(parse_result: ParseResult, 
                   source_file: str = "",
                   transition_length_mm: float = 0.0) -> SpliceRecipe:
    """
    Convenience function to generate a recipe.
    
    Args:
        parse_result: Result from GCodeParser
        source_file: Original filename
        transition_length_mm: Extra length for color transitions
        
    Returns:
        SpliceRecipe
    """
    generator = RecipeGenerator(transition_length_mm=transition_length_mm)
    return generator.generate(parse_result, source_file)
