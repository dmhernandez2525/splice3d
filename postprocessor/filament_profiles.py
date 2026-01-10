"""
Filament Profile Database for Splice3D

Contains splice parameters for different materials and brands.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FilamentProfile:
    """Profile for a specific filament material/brand combination."""
    name: str
    material: str
    brand: Optional[str] = None
    
    # Temperature settings (Celsius)
    splice_temp: int = 210
    
    # Timing (milliseconds)
    heat_time_ms: int = 3000
    cooling_time_ms: int = 5000
    
    # Mechanical (mm)
    compression_mm: float = 2.0
    
    # Compatibility
    compatible_with: list[str] = None  # List of compatible material names
    
    # Notes
    notes: str = ""
    
    def __post_init__(self):
        if self.compatible_with is None:
            self.compatible_with = [self.material]


# Default profiles for common materials
PROFILES = {
    # === PLA ===
    "pla": FilamentProfile(
        name="Generic PLA",
        material="PLA",
        splice_temp=210,
        heat_time_ms=3000,
        cooling_time_ms=5000,
        compression_mm=2.0,
        compatible_with=["PLA", "PLA+", "PLA Matte"],
        notes="Most common, easy to splice"
    ),
    
    "pla_bambu_matte": FilamentProfile(
        name="Bambu Lab Matte PLA",
        material="PLA",
        brand="Bambu Lab",
        splice_temp=215,
        heat_time_ms=3200,
        cooling_time_ms=5000,
        compression_mm=2.0,
        notes="Starry Night Vase colors"
    ),
    
    "pla_polymaker": FilamentProfile(
        name="Polymaker PolyTerra PLA",
        material="PLA",
        brand="Polymaker",
        splice_temp=205,
        heat_time_ms=2800,
        cooling_time_ms=4500,
        compression_mm=2.0,
        notes="Lower temp, matte finish"
    ),
    
    # === PETG ===
    "petg": FilamentProfile(
        name="Generic PETG",
        material="PETG",
        splice_temp=235,
        heat_time_ms=3500,
        cooling_time_ms=6000,
        compression_mm=2.5,
        compatible_with=["PETG"],
        notes="Higher temp than PLA, strong splices"
    ),
    
    "petg_overture": FilamentProfile(
        name="Overture PETG",
        material="PETG",
        brand="Overture",
        splice_temp=240,
        heat_time_ms=3500,
        cooling_time_ms=6000,
        compression_mm=2.5,
        notes="Popular budget PETG"
    ),
    
    # === ABS ===
    "abs": FilamentProfile(
        name="Generic ABS",
        material="ABS",
        splice_temp=250,
        heat_time_ms=4000,
        cooling_time_ms=7000,
        compression_mm=2.5,
        compatible_with=["ABS", "ASA"],
        notes="Requires good ventilation, fumes"
    ),
    
    # === ASA ===
    "asa": FilamentProfile(
        name="Generic ASA",
        material="ASA",
        splice_temp=255,
        heat_time_ms=4000,
        cooling_time_ms=7000,
        compression_mm=2.5,
        compatible_with=["ASA", "ABS"],
        notes="UV resistant, outdoor use"
    ),
    
    # === Specialty ===
    "pla_silk": FilamentProfile(
        name="Silk PLA",
        material="PLA",
        splice_temp=220,
        heat_time_ms=3500,
        cooling_time_ms=5500,
        compression_mm=2.0,
        compatible_with=["PLA", "PLA Silk"],
        notes="Higher temp for glossy finish"
    ),
    
    "pla_wood": FilamentProfile(
        name="Wood-fill PLA",
        material="PLA",
        splice_temp=200,
        heat_time_ms=2500,
        cooling_time_ms=4000,
        compression_mm=1.8,
        notes="Lower temp to prevent burning wood fibers"
    ),
}


def get_profile(name: str) -> Optional[FilamentProfile]:
    """Get a profile by name."""
    return PROFILES.get(name.lower())


def get_profile_for_material(material: str) -> Optional[FilamentProfile]:
    """Get default profile for a material type."""
    material_lower = material.lower()
    for profile in PROFILES.values():
        if profile.material.lower() == material_lower and profile.brand is None:
            return profile
    return None


def list_profiles() -> list[str]:
    """List all available profile names."""
    return list(PROFILES.keys())


def are_compatible(material_a: str, material_b: str) -> bool:
    """Check if two materials can be spliced together."""
    profile_a = get_profile_for_material(material_a)
    if profile_a is None:
        return False
    
    return material_b.upper() in [m.upper() for m in profile_a.compatible_with]


def get_splice_params(material_a: str, material_b: str) -> Optional[dict]:
    """
    Get optimal splice parameters for joining two materials.
    Uses the higher temperature of the two.
    """
    profile_a = get_profile_for_material(material_a)
    profile_b = get_profile_for_material(material_b)
    
    if profile_a is None or profile_b is None:
        return None
    
    if not are_compatible(material_a, material_b):
        return None
    
    # Use the higher/longer parameters for safety
    return {
        "splice_temp": max(profile_a.splice_temp, profile_b.splice_temp),
        "heat_time_ms": max(profile_a.heat_time_ms, profile_b.heat_time_ms),
        "cooling_time_ms": max(profile_a.cooling_time_ms, profile_b.cooling_time_ms),
        "compression_mm": max(profile_a.compression_mm, profile_b.compression_mm),
    }


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Available profiles:")
        for name, profile in PROFILES.items():
            print(f"  {name}: {profile.name} ({profile.material}, {profile.splice_temp}°C)")
    else:
        profile = get_profile(sys.argv[1])
        if profile:
            print(f"Profile: {profile.name}")
            print(f"  Material: {profile.material}")
            print(f"  Brand: {profile.brand or 'Generic'}")
            print(f"  Splice temp: {profile.splice_temp}°C")
            print(f"  Heat time: {profile.heat_time_ms}ms")
            print(f"  Cooling time: {profile.cooling_time_ms}ms")
            print(f"  Compression: {profile.compression_mm}mm")
            print(f"  Compatible with: {', '.join(profile.compatible_with)}")
            print(f"  Notes: {profile.notes}")
        else:
            print(f"Profile not found: {sys.argv[1]}")
