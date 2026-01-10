#!/usr/bin/env python3
"""
Splice3D Post-Processor

Main entry point for processing multi-color G-code.

Usage:
    python splice3d_postprocessor.py input.gcode [options]
    
    Options:
        -o, --output DIR        Output directory (default: same as input)
        -t, --transition MM     Transition length in mm (default: 0)
        --no-pause              Don't add pause at start
        -v, --verbose           Verbose output
"""

import argparse
import os
import sys
from pathlib import Path

from gcode_parser import GCodeParser, parse_gcode
from recipe_generator import RecipeGenerator, generate_recipe
from gcode_modifier import GCodeModifier, modify_gcode


def main():
    parser = argparse.ArgumentParser(
        description="Splice3D Post-Processor - Convert multi-color G-code for pre-spliced filament"
    )
    parser.add_argument(
        "input",
        help="Input G-code file (multi-tool)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: same as input file)",
        default=None
    )
    parser.add_argument(
        "-t", "--transition",
        type=float,
        default=0.0,
        help="Extra transition length in mm for color purging (default: 0)"
    )
    parser.add_argument(
        "--min-segment",
        type=float,
        default=10.0,
        help="Minimum segment length in mm (smaller segments merged, default: 10)"
    )
    parser.add_argument(
        "--no-pause",
        action="store_true",
        help="Don't add M0 pause at start of print"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--colors",
        nargs="+",
        help="Color names for tools (e.g., --colors white black red)"
    )
    
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Set up output paths
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = input_path.parent
    
    base_name = input_path.stem
    recipe_path = output_dir / f"{base_name}_splice_recipe.json"
    modified_gcode_path = output_dir / f"{base_name}_modified.gcode"
    
    print(f"Splice3D Post-Processor")
    print(f"=" * 40)
    print(f"Input: {input_path}")
    print()
    
    # Step 1: Parse G-code
    print("Parsing G-code...")
    gcode_parser = GCodeParser()
    parse_result = gcode_parser.parse_file(str(input_path))
    
    if parse_result.errors:
        for error in parse_result.errors:
            print(f"  ERROR: {error}", file=sys.stderr)
        sys.exit(1)
    
    for warning in parse_result.warnings:
        print(f"  WARNING: {warning}")
    
    print(f"  Found {len(parse_result.segments)} segments")
    print(f"  Total extrusion: {parse_result.total_length_mm:.1f} mm")
    print(f"  Colors used: {parse_result.color_count}")
    print(f"  Layers: {parse_result.layer_count}")
    
    if args.verbose:
        print()
        print("Segments:")
        for i, seg in enumerate(parse_result.segments[:20]):  # Limit output
            print(f"  {i+1}. Color {seg.color_index}: {seg.length_mm:.1f} mm (lines {seg.start_line}-{seg.end_line})")
        if len(parse_result.segments) > 20:
            print(f"  ... and {len(parse_result.segments) - 20} more")
    
    # Step 2: Generate recipe
    print()
    print("Generating splice recipe...")
    
    # Set up color names
    color_names = None
    if args.colors:
        color_names = {i: name for i, name in enumerate(args.colors)}
    
    recipe_gen = RecipeGenerator(
        color_names=color_names,
        transition_length_mm=args.transition,
        min_segment_length_mm=args.min_segment
    )
    recipe = recipe_gen.generate(parse_result, source_file=str(input_path))
    recipe_gen.save_recipe(recipe, str(recipe_path))
    
    print(f"  Recipe saved: {recipe_path}")
    print(f"  Final segments: {recipe.segment_count}")
    print(f"  Total filament needed: {recipe.total_length_mm:.1f} mm ({recipe.total_length_mm/1000:.2f} m)")
    
    # Step 3: Modify G-code
    print()
    print("Modifying G-code for single-extruder...")
    
    modifier = GCodeModifier(
        add_pause_at_start=not args.no_pause
    )
    stats = modifier.modify_file(str(input_path), str(modified_gcode_path))
    
    print(f"  Modified G-code saved: {modified_gcode_path}")
    print(f"  Tool changes removed: {stats['tool_changes_removed']}")
    
    # Summary
    print()
    print("=" * 40)
    print("Done! Next steps:")
    print(f"  1. Send recipe to Splice3D machine: {recipe_path.name}")
    print(f"  2. After splicing, print with: {modified_gcode_path.name}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
