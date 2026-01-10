"""
G-code Modifier for Splice3D

Modifies multi-tool G-code for single-extruder printing:
1. Removes tool change commands (T0, T1, etc.)
2. Keeps prime tower geometry
3. Adds note about using pre-spliced filament
"""

import re
from typing import Optional


class GCodeModifier:
    """
    Modifies G-code for single-extruder printing with pre-spliced filament.
    """
    
    TOOL_CHANGE_PATTERN = re.compile(r'^T\d+', re.IGNORECASE)
    
    def __init__(self, 
                 add_pause_at_start: bool = True,
                 pause_command: str = "M0"):
        """
        Initialize the modifier.
        
        Args:
            add_pause_at_start: Whether to add a pause for spool loading
            pause_command: G-code command for pause (M0 or M600)
        """
        self.add_pause_at_start = add_pause_at_start
        self.pause_command = pause_command
    
    def modify_file(self, input_path: str, output_path: str) -> dict:
        """
        Modify a G-code file for single-extruder printing.
        
        Args:
            input_path: Path to original multi-tool G-code
            output_path: Path for modified G-code
            
        Returns:
            Dictionary with statistics about modifications
        """
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        modified_lines, stats = self.modify_lines(lines)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
        
        return stats
    
    def modify_lines(self, lines: list[str]) -> tuple[list[str], dict]:
        """
        Modify G-code lines for single-extruder printing.
        
        Args:
            lines: Original G-code lines
            
        Returns:
            Tuple of (modified lines, statistics dict)
        """
        modified = []
        stats = {
            "tool_changes_removed": 0,
            "lines_modified": 0,
            "total_lines": len(lines)
        }
        
        # Add header
        header = self._generate_header()
        modified.extend(header)
        
        # Track if we've added the start pause
        pause_added = False
        found_start_gcode = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detect start of actual printing (after start G-code)
            if not found_start_gcode and stripped.startswith(';'):
                if 'END_GCODE' in stripped.upper() or 'START_GCODE' in stripped.upper():
                    found_start_gcode = True
            
            # Add pause before first move after start
            if (self.add_pause_at_start and 
                not pause_added and 
                found_start_gcode and
                (stripped.startswith('G0') or stripped.startswith('G1'))):
                modified.append(f"\n; === SPLICE3D: Load pre-spliced spool now ===\n")
                modified.append(f"{self.pause_command} ; Pause for spool loading\n")
                modified.append(f"; === Press continue when ready ===\n\n")
                pause_added = True
            
            # Remove tool change commands
            if self.TOOL_CHANGE_PATTERN.match(stripped):
                # Replace with comment
                modified.append(f"; SPLICE3D: Removed {stripped}\n")
                stats["tool_changes_removed"] += 1
                stats["lines_modified"] += 1
            else:
                modified.append(line)
        
        return modified, stats
    
    def _generate_header(self) -> list[str]:
        """Generate header comments for modified G-code."""
        return [
            "; ============================================\n",
            "; Modified by Splice3D Post-Processor\n",
            "; \n",
            "; This G-code has been modified for use with\n",
            "; pre-spliced multi-color filament.\n",
            "; \n",
            "; Tool change commands have been removed.\n",
            "; Load your Splice3D spool before printing.\n",
            "; ============================================\n",
            "\n"
        ]


def modify_gcode(input_path: str, output_path: str) -> dict:
    """
    Convenience function to modify G-code.
    
    Args:
        input_path: Path to original G-code
        output_path: Path for modified G-code
        
    Returns:
        Statistics about modifications
    """
    modifier = GCodeModifier()
    return modifier.modify_file(input_path, output_path)
