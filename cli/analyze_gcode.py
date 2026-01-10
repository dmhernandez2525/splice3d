"""
Splice3D G-code Analysis Tool

Analyzes multi-color G-code to provide statistics about segments,
color distribution, and estimated splice performance.

Usage:
    python analyze_gcode.py model.gcode [--output stats.json]
"""

import argparse
import json
import sys
from pathlib import Path
from collections import Counter
from dataclasses import dataclass, asdict

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "postprocessor"))

from gcode_parser import GCodeParser


@dataclass
class SegmentStats:
    """Statistics about segment lengths."""
    count: int = 0
    total_mm: float = 0.0
    min_mm: float = 0.0
    max_mm: float = 0.0
    avg_mm: float = 0.0
    median_mm: float = 0.0
    
    # Distribution buckets
    very_short: int = 0   # <5mm
    short: int = 0        # 5-20mm
    medium: int = 0       # 20-100mm
    long: int = 0         # 100-500mm
    very_long: int = 0    # >500mm


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    filename: str
    segment_stats: SegmentStats
    color_count: int
    color_distribution: dict
    layer_count: int
    estimated_splice_time_hours: float
    estimated_waste_reduction_percent: float
    warnings: list


def analyze_gcode(filepath: str) -> AnalysisResult:
    """
    Analyze G-code file and return statistics.
    
    Args:
        filepath: Path to G-code file
        
    Returns:
        AnalysisResult with all statistics
    """
    parser = GCodeParser()
    result = parser.parse_file(filepath)
    
    warnings = list(result.warnings)
    
    if not result.segments:
        return AnalysisResult(
            filename=filepath,
            segment_stats=SegmentStats(),
            color_count=0,
            color_distribution={},
            layer_count=0,
            estimated_splice_time_hours=0,
            estimated_waste_reduction_percent=0,
            warnings=warnings + ["No segments found"]
        )
    
    # Calculate segment statistics
    lengths = [s.length_mm for s in result.segments]
    lengths_sorted = sorted(lengths)
    
    stats = SegmentStats(
        count=len(lengths),
        total_mm=sum(lengths),
        min_mm=min(lengths),
        max_mm=max(lengths),
        avg_mm=sum(lengths) / len(lengths),
        median_mm=lengths_sorted[len(lengths) // 2]
    )
    
    # Distribution buckets
    for length in lengths:
        if length < 5:
            stats.very_short += 1
        elif length < 20:
            stats.short += 1
        elif length < 100:
            stats.medium += 1
        elif length < 500:
            stats.long += 1
        else:
            stats.very_long += 1
    
    # Color distribution
    color_counts = Counter(s.color_index for s in result.segments)
    color_distribution = {
        f"T{color}": count 
        for color, count in sorted(color_counts.items())
    }
    
    # Estimates
    # Assume 45 seconds per splice on average
    splice_time_hours = (stats.count * 45) / 3600
    
    # Traditional purge: ~50mm per change
    # Splice3D: ~10mm buffer per splice
    traditional_waste_mm = stats.count * 50
    splice3d_waste_mm = stats.count * 10
    waste_reduction = ((traditional_waste_mm - splice3d_waste_mm) / traditional_waste_mm) * 100
    
    # Add warnings for potential issues
    if stats.very_short > stats.count * 0.2:
        warnings.append(f"High proportion of very short segments ({stats.very_short}/{stats.count})")
    
    if stats.count > 5000:
        warnings.append(f"Very high segment count ({stats.count}) - consider simplifying")
    
    return AnalysisResult(
        filename=filepath,
        segment_stats=stats,
        color_count=result.color_count,
        color_distribution=color_distribution,
        layer_count=result.layer_count,
        estimated_splice_time_hours=round(splice_time_hours, 1),
        estimated_waste_reduction_percent=round(waste_reduction, 1),
        warnings=warnings
    )


def print_analysis(result: AnalysisResult):
    """Print analysis results in a readable format."""
    print(f"\n{'='*60}")
    print(f"SPLICE3D G-CODE ANALYSIS")
    print(f"{'='*60}")
    print(f"File: {result.filename}")
    print()
    
    stats = result.segment_stats
    
    print(f"SEGMENTS")
    print(f"  Total count: {stats.count}")
    print(f"  Total length: {stats.total_mm:.1f}mm ({stats.total_mm/1000:.2f}m)")
    print()
    
    print(f"SEGMENT LENGTHS")
    print(f"  Min: {stats.min_mm:.1f}mm")
    print(f"  Max: {stats.max_mm:.1f}mm")
    print(f"  Average: {stats.avg_mm:.1f}mm")
    print(f"  Median: {stats.median_mm:.1f}mm")
    print()
    
    print(f"LENGTH DISTRIBUTION")
    print(f"  Very short (<5mm): {stats.very_short} ({100*stats.very_short/max(1,stats.count):.1f}%)")
    print(f"  Short (5-20mm): {stats.short} ({100*stats.short/max(1,stats.count):.1f}%)")
    print(f"  Medium (20-100mm): {stats.medium} ({100*stats.medium/max(1,stats.count):.1f}%)")
    print(f"  Long (100-500mm): {stats.long} ({100*stats.long/max(1,stats.count):.1f}%)")
    print(f"  Very long (>500mm): {stats.very_long} ({100*stats.very_long/max(1,stats.count):.1f}%)")
    print()
    
    print(f"COLORS")
    print(f"  Color count: {result.color_count}")
    for tool, count in result.color_distribution.items():
        pct = 100 * count / max(1, stats.count)
        print(f"    {tool}: {count} segments ({pct:.1f}%)")
    print()
    
    print(f"ESTIMATES")
    print(f"  Layers: {result.layer_count}")
    print(f"  Splice prep time: ~{result.estimated_splice_time_hours:.1f} hours")
    print(f"  Waste reduction vs traditional: ~{result.estimated_waste_reduction_percent:.0f}%")
    print()
    
    if result.warnings:
        print(f"WARNINGS")
        for warning in result.warnings:
            print(f"  ⚠ {warning}")
        print()
    
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze multi-color G-code for Splice3D"
    )
    parser.add_argument(
        "gcode",
        help="Path to G-code file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Save results to JSON file"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Only output JSON (no console output)"
    )
    
    args = parser.parse_args()
    
    if not Path(args.gcode).exists():
        print(f"Error: File not found: {args.gcode}", file=sys.stderr)
        return 1
    
    result = analyze_gcode(args.gcode)
    
    if not args.quiet:
        print_analysis(result)
    
    if args.output:
        # Convert to JSON-serializable dict
        data = {
            "filename": result.filename,
            "segment_stats": asdict(result.segment_stats),
            "color_count": result.color_count,
            "color_distribution": result.color_distribution,
            "layer_count": result.layer_count,
            "estimated_splice_time_hours": result.estimated_splice_time_hours,
            "estimated_waste_reduction_percent": result.estimated_waste_reduction_percent,
            "warnings": result.warnings
        }
        
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2)
        
        if not args.quiet:
            print(f"Results saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
