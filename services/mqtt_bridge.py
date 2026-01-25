#!/usr/bin/env python3
"""
Splice3D MQTT Bridge Service

Bridges serial communication with the Splice3D machine to MQTT for Home Assistant integration.
Publishes status updates and subscribes to command topics.

Usage:
    python mqtt_bridge.py --port /dev/ttyUSB0 --mqtt-host localhost
    python mqtt_bridge.py --config /etc/splice3d/mqtt_bridge.yaml
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Optional

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: pyserial not installed. Run: pip install pyserial")
    sys.exit(1)

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("Error: paho-mqtt not installed. Run: pip install paho-mqtt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('splice3d-bridge')


# MQTT Topic Configuration
TOPIC_PREFIX = "home/splice3d"
TOPICS = {
    # Status topics (published by bridge)
    "state": f"{TOPIC_PREFIX}/status/state",
    "progress": f"{TOPIC_PREFIX}/status/progress/percent",
    "temp_current": f"{TOPIC_PREFIX}/status/temperature/current",
    "temp_target": f"{TOPIC_PREFIX}/status/temperature/target",
    "online": f"{TOPIC_PREFIX}/status/online",
    "segment": f"{TOPIC_PREFIX}/status/segment/current",
    "segments_total": f"{TOPIC_PREFIX}/status/segment/total",
    "error": f"{TOPIC_PREFIX}/status/error",
    "error_message": f"{TOPIC_PREFIX}/status/error_message",

    # Statistics topics
    "splices_today": f"{TOPIC_PREFIX}/stats/splices_today",
    "splices_total": f"{TOPIC_PREFIX}/stats/splices_total",
    "failures_today": f"{TOPIC_PREFIX}/stats/failures_today",
    "uptime": f"{TOPIC_PREFIX}/stats/uptime_seconds",

    # Command topics (subscribed by bridge)
    "cmd_start": f"{TOPIC_PREFIX}/command/start",
    "cmd_pause": f"{TOPIC_PREFIX}/command/pause",
    "cmd_resume": f"{TOPIC_PREFIX}/command/resume",
    "cmd_abort": f"{TOPIC_PREFIX}/command/abort",
    "cmd_preheat": f"{TOPIC_PREFIX}/command/preheat",
    "cmd_cooldown": f"{TOPIC_PREFIX}/command/cooldown",
}


@dataclass
class BridgeStats:
    """Statistics tracking for the bridge."""
    splices_today: int = 0
    splices_total: int = 0
    failures_today: int = 0
    failures_total: int = 0
    last_reset_date: str = field(default_factory=lambda: date.today().isoformat())
    start_time: float = field(default_factory=time.time)

    def reset_daily(self):
        """Reset daily counters if date has changed."""
        today = date.today().isoformat()
        if today != self.last_reset_date:
            logger.info(f"Resetting daily stats (was {self.last_reset_date}, now {today})")
            self.splices_today = 0
            self.failures_today = 0
            self.last_reset_date = today

    def record_splice(self):
        """Record a successful splice."""
        self.reset_daily()
        self.splices_today += 1
        self.splices_total += 1

    def record_failure(self):
        """Record a failure."""
        self.reset_daily()
        self.failures_today += 1
        self.failures_total += 1

    @property
    def uptime_seconds(self) -> int:
        """Get uptime in seconds."""
        return int(time.time() - self.start_time)

    def to_dict(self) -> dict:
        """Convert to dictionary for persistence."""
        return {
            "splices_today": self.splices_today,
            "splices_total": self.splices_total,
            "failures_today": self.failures_today,
            "failures_total": self.failures_total,
            "last_reset_date": self.last_reset_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BridgeStats":
        """Create from dictionary."""
        stats = cls()
        stats.splices_total = data.get("splices_total", 0)
        stats.failures_total = data.get("failures_total", 0)
        stats.last_reset_date = data.get("last_reset_date", date.today().isoformat())
        # Daily stats are reset on load
        stats.reset_daily()
        return stats


@dataclass
class MachineState:
    """Current state of the Splice3D machine."""
    state: str = "OFFLINE"
    progress: int = 0
    current_segment: int = 0
    total_segments: int = 0
    temperature_current: float = 0.0
    temperature_target: float = 0.0
    error: bool = False
    error_message: str = ""
    last_update: float = field(default_factory=time.time)


class Splice3DMQTTBridge:
    """MQTT Bridge for Splice3D machine."""

    def __init__(
        self,
        serial_port: str,
        serial_baud: int = 115200,
        mqtt_host: str = "localhost",
        mqtt_port: int = 1883,
        mqtt_username: Optional[str] = None,
        mqtt_password: Optional[str] = None,
        mqtt_client_id: str = "splice3d-bridge",
        stats_file: Optional[Path] = None,
    ):
        self.serial_port = serial_port
        self.serial_baud = serial_baud
        self.serial: Optional[serial.Serial] = None

        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.mqtt_client_id = mqtt_client_id
        self.mqtt_client: Optional[mqtt.Client] = None

        self.stats_file = stats_file or Path("/var/lib/splice3d/stats.json")
        self.stats = self._load_stats()
        self.state = MachineState()

        self.running = False
        self.reconnect_delay = 5
        self._serial_lock = threading.Lock()

    def _load_stats(self) -> BridgeStats:
        """Load statistics from file."""
        try:
            if self.stats_file.exists():
                with open(self.stats_file) as f:
                    return BridgeStats.from_dict(json.load(f))
        except Exception as e:
            logger.warning(f"Could not load stats: {e}")
        return BridgeStats()

    def _save_stats(self):
        """Save statistics to file."""
        try:
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Could not save stats: {e}")

    def _on_mqtt_connect(self, client, userdata, flags, rc, properties=None):
        """Handle MQTT connection."""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to command topics
            for topic_key in TOPICS:
                if topic_key.startswith("cmd_"):
                    topic = TOPICS[topic_key]
                    client.subscribe(topic)
                    logger.debug(f"Subscribed to {topic}")
            # Publish online status
            self._publish_state()
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_mqtt_disconnect(self, client, userdata, rc, properties=None):
        """Handle MQTT disconnection."""
        logger.warning(f"Disconnected from MQTT broker (rc={rc})")

    def _on_mqtt_message(self, client, userdata, msg):
        """Handle incoming MQTT messages (commands)."""
        topic = msg.topic
        payload = msg.payload.decode('utf-8', errors='replace').strip()

        logger.info(f"Received command: {topic} = {payload}")

        # Map topics to commands
        topic_to_cmd = {
            TOPICS["cmd_start"]: "START",
            TOPICS["cmd_pause"]: "PAUSE",
            TOPICS["cmd_resume"]: "RESUME",
            TOPICS["cmd_abort"]: "ABORT",
            TOPICS["cmd_preheat"]: "PREHEAT",
            TOPICS["cmd_cooldown"]: "COOLDOWN",
        }

        if topic in topic_to_cmd:
            cmd = topic_to_cmd[topic]
            # Add payload as argument if present
            if payload and payload != "1":
                cmd = f"{cmd} {payload}"
            self._send_serial_command(cmd)

    def _send_serial_command(self, command: str) -> list[str]:
        """Send command to serial port and return responses."""
        if not self.serial or not self.serial.is_open:
            logger.error("Serial port not connected")
            return []

        with self._serial_lock:
            try:
                self.serial.write(f"{command}\n".encode('utf-8'))
                self.serial.flush()

                responses = []
                start_time = time.time()
                timeout = 2.0

                while time.time() - start_time < timeout:
                    if self.serial.in_waiting:
                        line = self.serial.readline().decode('utf-8', errors='replace').strip()
                        if line:
                            responses.append(line)
                            if line.startswith('OK') or line.startswith('ERROR'):
                                break
                    else:
                        time.sleep(0.01)

                logger.debug(f"Command '{command}' -> {responses}")
                return responses

            except serial.SerialException as e:
                logger.error(f"Serial error: {e}")
                return []

    def _parse_status_line(self, line: str):
        """Parse a status line from the machine and update state."""
        # Status format: STATE:IDLE TEMP:200/210 PROGRESS:0 SEGMENT:0/0
        parts = line.split()

        for part in parts:
            if ':' not in part:
                continue

            key, value = part.split(':', 1)
            key = key.upper()

            if key == "STATE":
                self.state.state = value
            elif key == "TEMP":
                if '/' in value:
                    current, target = value.split('/')
                    self.state.temperature_current = float(current)
                    self.state.temperature_target = float(target)
            elif key == "PROGRESS":
                self.state.progress = int(value)
            elif key == "SEGMENT":
                if '/' in value:
                    current, total = value.split('/')
                    self.state.current_segment = int(current)
                    self.state.total_segments = int(total)
            elif key == "ERROR":
                self.state.error = True
                self.state.error_message = value

        self.state.last_update = time.time()

    def _handle_serial_line(self, line: str):
        """Handle a line received from serial."""
        logger.debug(f"Serial: {line}")

        if line.startswith("STATUS:") or "STATE:" in line:
            self._parse_status_line(line)
            self._publish_state()

        elif line.startswith("PROGRESS:"):
            try:
                self.state.progress = int(line.split(':')[1])
                self._publish_state()
            except ValueError:
                pass

        elif line.startswith("DONE"):
            self.state.state = "IDLE"
            self.state.progress = 100
            self.stats.record_splice()
            self._save_stats()
            self._publish_state()
            self._publish_stats()
            logger.info("Splice completed successfully")

        elif line.startswith("ERROR"):
            self.state.error = True
            self.state.error_message = line[6:].strip() if len(line) > 6 else "Unknown error"
            self.state.state = "ERROR"
            self.stats.record_failure()
            self._save_stats()
            self._publish_state()
            self._publish_stats()
            logger.error(f"Machine error: {self.state.error_message}")

        elif line.startswith("TEMP:"):
            # Temperature update: TEMP:200/210
            try:
                temps = line[5:].split('/')
                self.state.temperature_current = float(temps[0])
                if len(temps) > 1:
                    self.state.temperature_target = float(temps[1])
                self._publish_state()
            except (ValueError, IndexError):
                pass

    def _publish_state(self):
        """Publish current state to MQTT."""
        if not self.mqtt_client or not self.mqtt_client.is_connected():
            return

        try:
            self.mqtt_client.publish(TOPICS["state"], self.state.state, retain=True)
            self.mqtt_client.publish(TOPICS["progress"], self.state.progress, retain=True)
            self.mqtt_client.publish(TOPICS["temp_current"], self.state.temperature_current, retain=True)
            self.mqtt_client.publish(TOPICS["temp_target"], self.state.temperature_target, retain=True)
            self.mqtt_client.publish(TOPICS["segment"], self.state.current_segment, retain=True)
            self.mqtt_client.publish(TOPICS["segments_total"], self.state.total_segments, retain=True)
            self.mqtt_client.publish(TOPICS["error"], "ON" if self.state.error else "OFF", retain=True)
            self.mqtt_client.publish(TOPICS["error_message"], self.state.error_message, retain=True)

            # Online status - only published when connected
            online = self.serial and self.serial.is_open and self.state.state != "OFFLINE"
            self.mqtt_client.publish(TOPICS["online"], "ON" if online else "OFF", retain=True)

        except Exception as e:
            logger.error(f"Error publishing state: {e}")

    def _publish_stats(self):
        """Publish statistics to MQTT."""
        if not self.mqtt_client or not self.mqtt_client.is_connected():
            return

        try:
            self.stats.reset_daily()
            self.mqtt_client.publish(TOPICS["splices_today"], self.stats.splices_today, retain=True)
            self.mqtt_client.publish(TOPICS["splices_total"], self.stats.splices_total, retain=True)
            self.mqtt_client.publish(TOPICS["failures_today"], self.stats.failures_today, retain=True)
            self.mqtt_client.publish(TOPICS["uptime"], self.stats.uptime_seconds, retain=True)
        except Exception as e:
            logger.error(f"Error publishing stats: {e}")

    def _connect_serial(self) -> bool:
        """Connect to serial port."""
        try:
            self.serial = serial.Serial(
                port=self.serial_port,
                baudrate=self.serial_baud,
                timeout=0.1
            )
            # Wait for Arduino reset
            time.sleep(2)

            # Drain any startup messages
            while self.serial.in_waiting:
                self.serial.readline()

            logger.info(f"Connected to serial port {self.serial_port}")

            # Query initial status
            self._send_serial_command("STATUS")

            return True

        except serial.SerialException as e:
            logger.error(f"Serial connection failed: {e}")
            return False

    def _connect_mqtt(self) -> bool:
        """Connect to MQTT broker."""
        try:
            self.mqtt_client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=self.mqtt_client_id
            )

            if self.mqtt_username:
                self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)

            # Set up callbacks
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self.mqtt_client.on_message = self._on_mqtt_message

            # Set Last Will Testament (LWT) for offline detection
            self.mqtt_client.will_set(TOPICS["online"], "OFF", retain=True)

            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            self.mqtt_client.loop_start()

            logger.info(f"Connected to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
            return True

        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            return False

    def _serial_read_loop(self):
        """Background thread for reading serial data."""
        while self.running:
            if not self.serial or not self.serial.is_open:
                time.sleep(self.reconnect_delay)
                if self.running:
                    logger.info("Attempting serial reconnection...")
                    self._connect_serial()
                continue

            try:
                if self.serial.in_waiting:
                    with self._serial_lock:
                        line = self.serial.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        self._handle_serial_line(line)
                else:
                    time.sleep(0.01)
            except serial.SerialException as e:
                logger.error(f"Serial read error: {e}")
                self.state.state = "OFFLINE"
                self._publish_state()
                if self.serial:
                    try:
                        self.serial.close()
                    except:
                        pass
                    self.serial = None

    def _status_poll_loop(self):
        """Background thread for periodic status polling."""
        poll_interval = 5.0  # seconds
        stats_interval = 60.0  # seconds
        last_stats = time.time()

        while self.running:
            time.sleep(poll_interval)

            if self.running and self.serial and self.serial.is_open:
                responses = self._send_serial_command("STATUS")
                for line in responses:
                    self._handle_serial_line(line)

            # Publish stats less frequently
            if time.time() - last_stats >= stats_interval:
                self._publish_stats()
                last_stats = time.time()

    def run(self):
        """Main run loop."""
        logger.info("Starting Splice3D MQTT Bridge")

        # Set up signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.running = False

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        # Connect to serial
        if not self._connect_serial():
            logger.warning("Initial serial connection failed, will retry...")

        # Connect to MQTT
        if not self._connect_mqtt():
            logger.error("Could not connect to MQTT broker")
            return 1

        self.running = True

        # Start background threads
        serial_thread = threading.Thread(target=self._serial_read_loop, daemon=True)
        poll_thread = threading.Thread(target=self._status_poll_loop, daemon=True)

        serial_thread.start()
        poll_thread.start()

        logger.info("Bridge running. Press Ctrl+C to stop.")

        # Main loop
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

        # Cleanup
        logger.info("Shutting down...")
        self.running = False

        # Publish offline status
        self.state.state = "OFFLINE"
        self._publish_state()

        # Save stats
        self._save_stats()

        # Disconnect
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

        if self.serial and self.serial.is_open:
            self.serial.close()

        logger.info("Shutdown complete")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Splice3D MQTT Bridge - Home Assistant Integration"
    )
    parser.add_argument(
        "-p", "--port",
        default=os.environ.get("SPLICE3D_SERIAL_PORT", "/dev/ttyUSB0"),
        help="Serial port (default: $SPLICE3D_SERIAL_PORT or /dev/ttyUSB0)"
    )
    parser.add_argument(
        "-b", "--baud",
        type=int,
        default=int(os.environ.get("SPLICE3D_SERIAL_BAUD", "115200")),
        help="Baud rate (default: 115200)"
    )
    parser.add_argument(
        "--mqtt-host",
        default=os.environ.get("MQTT_HOST", "localhost"),
        help="MQTT broker host (default: $MQTT_HOST or localhost)"
    )
    parser.add_argument(
        "--mqtt-port",
        type=int,
        default=int(os.environ.get("MQTT_PORT", "1883")),
        help="MQTT broker port (default: 1883)"
    )
    parser.add_argument(
        "--mqtt-username",
        default=os.environ.get("MQTT_USERNAME"),
        help="MQTT username (default: $MQTT_USERNAME)"
    )
    parser.add_argument(
        "--mqtt-password",
        default=os.environ.get("MQTT_PASSWORD"),
        help="MQTT password (default: $MQTT_PASSWORD)"
    )
    parser.add_argument(
        "--stats-file",
        type=Path,
        default=Path(os.environ.get("SPLICE3D_STATS_FILE", "/var/lib/splice3d/stats.json")),
        help="Path to statistics file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "-l", "--list-ports",
        action="store_true",
        help="List available serial ports and exit"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.list_ports:
        print("Available serial ports:")
        for port in serial.tools.list_ports.comports():
            print(f"  {port.device}: {port.description}")
        return 0

    bridge = Splice3DMQTTBridge(
        serial_port=args.port,
        serial_baud=args.baud,
        mqtt_host=args.mqtt_host,
        mqtt_port=args.mqtt_port,
        mqtt_username=args.mqtt_username,
        mqtt_password=args.mqtt_password,
        stats_file=args.stats_file,
    )

    return bridge.run()


if __name__ == "__main__":
    sys.exit(main())
