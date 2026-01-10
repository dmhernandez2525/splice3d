#!/usr/bin/env python3
"""
Splice3D CLI - USB Communication Tool

Send splice recipes to the Splice3D machine and monitor progress.

Usage:
    python splice3d_cli.py --port /dev/ttyUSB0 --recipe recipe.json
    python splice3d_cli.py --port /dev/ttyUSB0 --monitor
    python splice3d_cli.py --port /dev/ttyUSB0 --command STATUS
"""

import argparse
import json
import sys
import time

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: pyserial not installed. Run: pip install pyserial")
    sys.exit(1)


class Splice3DCli:
    """CLI interface for Splice3D machine."""
    
    def __init__(self, port: str, baud: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.serial = None
    
    def connect(self) -> bool:
        """Connect to the Splice3D machine."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=self.timeout
            )
            # Wait for Arduino reset
            time.sleep(2)
            
            # Read startup message
            while self.serial.in_waiting:
                line = self.serial.readline().decode('utf-8', errors='replace').strip()
                print(f"< {line}")
            
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the machine."""
        if self.serial:
            self.serial.close()
            self.serial = None
    
    def send_command(self, command: str) -> list[str]:
        """Send a command and return response lines."""
        if not self.serial:
            return []
        
        self.serial.write(f"{command}\n".encode('utf-8'))
        self.serial.flush()
        
        responses = []
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            if self.serial.in_waiting:
                line = self.serial.readline().decode('utf-8', errors='replace').strip()
                if line:
                    responses.append(line)
                    # Break on terminal responses
                    if line.startswith('OK') or line.startswith('ERROR'):
                        break
            else:
                time.sleep(0.01)
        
        return responses
    
    def send_recipe(self, recipe_path: str) -> bool:
        """Send a splice recipe to the machine."""
        try:
            with open(recipe_path, 'r') as f:
                recipe = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading recipe: {e}")
            return False
        
        # Convert to compact JSON for transmission
        compact = json.dumps(recipe, separators=(',', ':'))
        
        print(f"Sending recipe ({len(recipe.get('segments', []))} segments)...")
        responses = self.send_command(f"RECIPE {compact}")
        
        for line in responses:
            print(f"< {line}")
        
        return any('OK' in r for r in responses)
    
    def start_splicing(self) -> bool:
        """Send START command."""
        responses = self.send_command("START")
        for line in responses:
            print(f"< {line}")
        return any('OK' in r or 'STARTED' in r for r in responses)
    
    def get_status(self) -> str:
        """Query current status."""
        responses = self.send_command("STATUS")
        return responses[0] if responses else "NO RESPONSE"
    
    def monitor(self, interval: float = 0.5):
        """Monitor machine progress until complete or interrupted."""
        print("Monitoring progress (Ctrl+C to stop)...")
        
        try:
            while True:
                # Check for any incoming data
                while self.serial.in_waiting:
                    line = self.serial.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        print(f"< {line}")
                        if line.startswith('DONE'):
                            return
                        if line.startswith('ERROR'):
                            return
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")


def list_ports():
    """List available serial ports."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
    else:
        print("Available ports:")
        for port in ports:
            print(f"  {port.device}: {port.description}")


def main():
    parser = argparse.ArgumentParser(
        description="Splice3D CLI - USB Communication Tool"
    )
    parser.add_argument(
        "-p", "--port",
        help="Serial port (e.g., /dev/ttyUSB0 or COM3)"
    )
    parser.add_argument(
        "-b", "--baud",
        type=int,
        default=115200,
        help="Baud rate (default: 115200)"
    )
    parser.add_argument(
        "-r", "--recipe",
        help="Path to splice recipe JSON file"
    )
    parser.add_argument(
        "-c", "--command",
        help="Send a single command"
    )
    parser.add_argument(
        "-m", "--monitor",
        action="store_true",
        help="Monitor machine progress"
    )
    parser.add_argument(
        "-s", "--start",
        action="store_true",
        help="Start splicing after sending recipe"
    )
    parser.add_argument(
        "-l", "--list-ports",
        action="store_true",
        help="List available serial ports"
    )
    
    args = parser.parse_args()
    
    if args.list_ports:
        list_ports()
        return 0
    
    if not args.port:
        print("Error: --port is required. Use --list-ports to see available ports.")
        return 1
    
    cli = Splice3DCli(args.port, args.baud)
    
    if not cli.connect():
        return 1
    
    try:
        if args.recipe:
            if not cli.send_recipe(args.recipe):
                return 1
            
            if args.start:
                if not cli.start_splicing():
                    return 1
                
                if args.monitor:
                    cli.monitor()
        
        elif args.command:
            responses = cli.send_command(args.command)
            for line in responses:
                print(f"< {line}")
        
        elif args.monitor:
            cli.monitor()
        
        else:
            # Interactive mode
            print("Interactive mode. Type 'help' for commands, 'quit' to exit.")
            while True:
                try:
                    cmd = input("> ").strip()
                    if not cmd:
                        continue
                    if cmd.lower() in ('quit', 'exit', 'q'):
                        break
                    
                    responses = cli.send_command(cmd)
                    for line in responses:
                        print(f"< {line}")
                except EOFError:
                    break
    
    finally:
        cli.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
