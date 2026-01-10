"""
G-code Parser for Splice3D

Parses multi-tool G-code and extracts:
- Tool change events (T0, T1, etc.)
- Extrusion lengths per segment
- Layer information
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Segment:
    """A segment of filament for one color."""
    color_index: int
    length_mm: float
    start_line: int
    end_line: int
    layer_start: Optional[int] = None
    layer_end: Optional[int] = None


@dataclass
class ParseResult:
    """Result of parsing a G-code file."""
    segments: list[Segment] = field(default_factory=list)
    total_length_mm: float = 0.0
    color_count: int = 0
    layer_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class GCodeParser:
    """
    Parser for multi-tool G-code files.
    
    Supports OrcaSlicer, PrusaSlicer, and BambuStudio G-code formats.
    """
    
    # Regex patterns for G-code parsing
    TOOL_CHANGE_PATTERN = re.compile(r'^T(\d+)', re.IGNORECASE)
    M600_PATTERN = re.compile(r'^M600', re.IGNORECASE)  # Color change command
    EXTRUSION_PATTERN = re.compile(r'E([-+]?\d*\.?\d+)', re.IGNORECASE)
    LAYER_PATTERN = re.compile(r';LAYER:(\d+)|;LAYER_CHANGE', re.IGNORECASE)
    MOVE_PATTERN = re.compile(r'^G[01]\s', re.IGNORECASE)
    
    def __init__(self, filament_diameter: float = 1.75):
        """
        Initialize the parser.
        
        Args:
            filament_diameter: Filament diameter in mm (default 1.75)
        """
        self.filament_diameter = filament_diameter
        self._reset_state()
    
    def _reset_state(self):
        """Reset parser state for a new file."""
        self.current_tool: int = 0
        self.current_e: float = 0.0
        self.segment_start_e: float = 0.0
        self.segment_start_line: int = 0
        self.current_layer: int = 0
        self.segment_start_layer: int = 0
        self.absolute_e: bool = True  # Track E mode (absolute vs relative)
        self.seen_tools: set[int] = set()
    
    def parse_file(self, filepath: str) -> ParseResult:
        """
        Parse a G-code file and extract splice segments.
        
        Args:
            filepath: Path to the G-code file
            
        Returns:
            ParseResult with segments and metadata
        """
        self._reset_state()
        result = ParseResult()
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except IOError as e:
            result.errors.append(f"Failed to read file: {e}")
            return result
        
        return self.parse_lines(lines)
    
    def parse_lines(self, lines: list[str]) -> ParseResult:
        """
        Parse G-code lines and extract splice segments.
        
        Args:
            lines: List of G-code lines
            
        Returns:
            ParseResult with segments and metadata
        """
        self._reset_state()
        result = ParseResult()
        
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            
            # Skip empty lines and pure comments
            if not line or line.startswith(';'):
                # Check for layer comments
                layer_match = self.LAYER_PATTERN.search(line)
                if layer_match:
                    if layer_match.group(1):
                        self.current_layer = int(layer_match.group(1))
                    else:
                        self.current_layer += 1
                continue
            
            # Check for absolute/relative E mode
            if line.startswith('M82'):
                self.absolute_e = True
                continue
            elif line.startswith('M83'):
                self.absolute_e = False
                continue
            
            # Check for tool change
            tool_match = self.TOOL_CHANGE_PATTERN.match(line)
            if tool_match:
                new_tool = int(tool_match.group(1))
                
                # Record segment if we've extruded anything
                if self.current_e > self.segment_start_e or self.seen_tools:
                    segment = self._create_segment(line_num - 1)
                    if segment.length_mm > 0:
                        result.segments.append(segment)
                
                # Start new segment
                self.current_tool = new_tool
                self.seen_tools.add(new_tool)
                self.segment_start_e = self.current_e
                self.segment_start_line = line_num
                self.segment_start_layer = self.current_layer
                continue
            
            # Check for M600 color change (alternate to tool change)
            if self.M600_PATTERN.match(line):
                # Record current segment
                if self.current_e > self.segment_start_e:
                    segment = self._create_segment(line_num - 1)
                    if segment.length_mm > 0:
                        result.segments.append(segment)
                
                # Toggle to next color (assumes 2-color for M600)
                self.current_tool = (self.current_tool + 1) % 2
                self.seen_tools.add(self.current_tool)
                self.segment_start_e = self.current_e
                self.segment_start_line = line_num
                self.segment_start_layer = self.current_layer
                continue
            
            # Check for extrusion moves
            if self.MOVE_PATTERN.match(line):
                e_match = self.EXTRUSION_PATTERN.search(line)
                if e_match:
                    e_value = float(e_match.group(1))
                    
                    if self.absolute_e:
                        # Absolute mode: E value is total extrusion
                        if e_value > self.current_e:
                            self.current_e = e_value
                    else:
                        # Relative mode: E value is delta
                        if e_value > 0:
                            self.current_e += e_value
            
            # Check for E reset (G92 E0)
            if line.startswith('G92'):
                e_match = self.EXTRUSION_PATTERN.search(line)
                if e_match:
                    new_e = float(e_match.group(1))
                    # Adjust segment start to account for reset
                    self.segment_start_e = self.segment_start_e - self.current_e + new_e
                    self.current_e = new_e
        
        # Capture final segment
        if self.current_e > self.segment_start_e:
            segment = self._create_segment(len(lines))
            if segment.length_mm > 0:
                result.segments.append(segment)
        
        # Calculate totals
        result.total_length_mm = sum(s.length_mm for s in result.segments)
        result.color_count = len(self.seen_tools) if self.seen_tools else 1
        result.layer_count = self.current_layer + 1
        
        # Validate
        if not result.segments:
            result.warnings.append("No extrusion segments found")
        if result.color_count < 2:
            result.warnings.append("Single color detected - no splicing needed")
        
        return result
    
    def _create_segment(self, end_line: int) -> Segment:
        """Create a segment from current state."""
        length = self.current_e - self.segment_start_e
        
        return Segment(
            color_index=self.current_tool,
            length_mm=round(length, 2),
            start_line=self.segment_start_line,
            end_line=end_line,
            layer_start=self.segment_start_layer,
            layer_end=self.current_layer
        )


def parse_gcode(filepath: str) -> ParseResult:
    """
    Convenience function to parse a G-code file.
    
    Args:
        filepath: Path to the G-code file
        
    Returns:
        ParseResult with segments and metadata
    """
    parser = GCodeParser()
    return parser.parse_file(filepath)
