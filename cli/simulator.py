#!/usr/bin/env python3
"""
Splice3D Firmware Simulator

Simulates the firmware state machine for testing without hardware.
Reads a splice recipe and logs what the machine would do.

Usage:
    python simulator.py recipe.json [--speed FACTOR]
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class State(Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    READY = "READY"
    FEEDING_A = "FEEDING_A"
    FEEDING_B = "FEEDING_B"
    CUTTING = "CUTTING"
    POSITIONING = "POSITIONING"
    HEATING = "HEATING"
    WELDING = "WELDING"
    COOLING = "COOLING"
    SPOOLING = "SPOOLING"
    NEXT_SEGMENT = "NEXT_SEGMENT"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


@dataclass
class SimConfig:
    """Simulation configuration."""
    feed_rate_mm_s: float = 50.0      # Filament feed speed
    weld_temp_c: float = 210.0        # Weld temperature
    heat_rate_c_s: float = 5.0        # Heating rate
    cool_rate_c_s: float = 10.0       # Cooling rate
    cut_time_s: float = 0.5           # Cutter actuation time
    position_time_s: float = 1.0      # Position alignment time
    weld_hold_s: float = 3.0          # Weld hold time
    cool_target_c: float = 50.0       # Cooling target
    speed_factor: float = 1.0         # Simulation speed multiplier


class FirmwareSimulator:
    """Simulates Splice3D firmware behavior."""
    
    def __init__(self, config: Optional[SimConfig] = None):
        self.config = config or SimConfig()
        self.state = State.IDLE
        self.segments = []
        self.current_segment = 0
        self.current_temp = 25.0
        self.total_filament_mm = 0.0
        self.total_time_s = 0.0
        self.splices_completed = 0
    
    def load_recipe(self, recipe_path: str) -> bool:
        """Load a splice recipe from JSON file."""
        try:
            with open(recipe_path, 'r') as f:
                data = json.load(f)
            
            self.segments = data.get('segments', [])
            self.current_segment = 0
            self.state = State.READY
            
            print(f"[LOAD] Recipe loaded: {len(self.segments)} segments")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load recipe: {e}")
            self.state = State.ERROR
            return False
    
    def run(self) -> bool:
        """Run the full simulation."""
        if self.state != State.READY:
            print("[ERROR] Not ready - load recipe first")
            return False
        
        print(f"\n{'='*60}")
        print("SPLICE3D SIMULATION")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        while self.state not in [State.COMPLETE, State.ERROR]:
            self._step()
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*60}")
        print("SIMULATION COMPLETE")
        print(f"{'='*60}")
        print(f"  Real time elapsed: {elapsed:.1f}s")
        print(f"  Simulated time: {self.total_time_s:.1f}s ({self.total_time_s/60:.1f} min)")
        print(f"  Total filament: {self.total_filament_mm:.1f}mm ({self.total_filament_mm/1000:.2f}m)")
        print(f"  Splices completed: {self.splices_completed}")
        
        return self.state == State.COMPLETE
    
    def _step(self):
        """Execute one state machine step."""
        if self.state == State.READY:
            print("[START] Beginning splice sequence")
            self._transition_to_feeding()
        
        elif self.state == State.FEEDING_A:
            seg = self.segments[self.current_segment]
            length = seg['length_mm']
            feed_time = length / self.config.feed_rate_mm_s
            
            print(f"[FEED_A] Feeding {length:.1f}mm of color 0 ({feed_time:.1f}s)")
            self._simulate_time(feed_time)
            self.total_filament_mm += length
            
            self.state = State.CUTTING
        
        elif self.state == State.FEEDING_B:
            seg = self.segments[self.current_segment]
            length = seg['length_mm']
            feed_time = length / self.config.feed_rate_mm_s
            
            print(f"[FEED_B] Feeding {length:.1f}mm of color 1 ({feed_time:.1f}s)")
            self._simulate_time(feed_time)
            self.total_filament_mm += length
            
            self.state = State.CUTTING
        
        elif self.state == State.CUTTING:
            print(f"[CUT] Activating cutter ({self.config.cut_time_s}s)")
            self._simulate_time(self.config.cut_time_s)
            self.state = State.POSITIONING
        
        elif self.state == State.POSITIONING:
            print(f"[POSITION] Aligning filaments ({self.config.position_time_s}s)")
            self._simulate_time(self.config.position_time_s)
            self.state = State.HEATING
        
        elif self.state == State.HEATING:
            temp_diff = self.config.weld_temp_c - self.current_temp
            heat_time = temp_diff / self.config.heat_rate_c_s
            
            print(f"[HEAT] Heating to {self.config.weld_temp_c}°C ({heat_time:.1f}s)")
            self._simulate_time(heat_time)
            self.current_temp = self.config.weld_temp_c
            
            self.state = State.WELDING
        
        elif self.state == State.WELDING:
            print(f"[WELD] Compressing and holding ({self.config.weld_hold_s}s)")
            self._simulate_time(self.config.weld_hold_s)
            self.splices_completed += 1
            
            self.state = State.COOLING
        
        elif self.state == State.COOLING:
            temp_diff = self.current_temp - self.config.cool_target_c
            cool_time = temp_diff / self.config.cool_rate_c_s
            
            print(f"[COOL] Cooling to {self.config.cool_target_c}°C ({cool_time:.1f}s)")
            self._simulate_time(cool_time)
            self.current_temp = self.config.cool_target_c
            
            self.state = State.SPOOLING
        
        elif self.state == State.SPOOLING:
            seg = self.segments[self.current_segment]
            length = seg['length_mm']
            spool_time = length / (self.config.feed_rate_mm_s * 1.5)  # Winder is faster
            
            print(f"[SPOOL] Winding {length:.1f}mm ({spool_time:.1f}s)")
            self._simulate_time(spool_time)
            
            self.state = State.NEXT_SEGMENT
        
        elif self.state == State.NEXT_SEGMENT:
            self.current_segment += 1
            
            if self.current_segment >= len(self.segments):
                print(f"[DONE] All segments complete!")
                self.state = State.COMPLETE
            else:
                print(f"\n--- Segment {self.current_segment + 1}/{len(self.segments)} ---")
                self._transition_to_feeding()
    
    def _transition_to_feeding(self):
        """Transition to appropriate feeding state based on color."""
        seg = self.segments[self.current_segment]
        color = seg.get('color', 0)
        
        if color == 0:
            self.state = State.FEEDING_A
        else:
            self.state = State.FEEDING_B
    
    def _simulate_time(self, seconds: float):
        """Simulate time passing (optionally with real delays)."""
        adjusted = seconds / self.config.speed_factor
        self.total_time_s += seconds
        
        # Add small real delay for visual effect (capped at 0.1s)
        if adjusted > 0:
            time.sleep(min(adjusted, 0.1))


def main():
    parser = argparse.ArgumentParser(
        description="Splice3D Firmware Simulator"
    )
    parser.add_argument(
        "recipe",
        help="Path to splice recipe JSON file"
    )
    parser.add_argument(
        "--speed", "-s",
        type=float,
        default=100.0,
        help="Simulation speed factor (default: 100x)"
    )
    parser.add_argument(
        "--temp",
        type=float,
        default=210.0,
        help="Weld temperature in Celsius"
    )
    parser.add_argument(
        "--feed-rate",
        type=float,
        default=50.0,
        help="Feed rate in mm/s"
    )
    
    args = parser.parse_args()
    
    config = SimConfig(
        speed_factor=args.speed,
        weld_temp_c=args.temp,
        feed_rate_mm_s=args.feed_rate
    )
    
    sim = FirmwareSimulator(config)
    
    if not sim.load_recipe(args.recipe):
        return 1
    
    if not sim.run():
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
