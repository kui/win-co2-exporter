import logging
import os
import time

import hid
from prometheus_client import Gauge, start_http_server

# Metrics
CO2_LEVEL = Gauge("co2mini_co2_ppm", "CO2 concentration in ppm")
TEMP_LEVEL = Gauge("co2mini_temperature_celsius", "Temperature in Celsius")

# Device Info
VID = 0x04D9
PID = 0xA052
MAGIC_KEY = [0x86, 0x41, 0xC9, 0xA8, 0x7F, 0x41, 0x3C, 0xCA]

# Exporter Configuration
EXPORTER_PORT = int(os.getenv("CO2_EXPORTER_PORT", "4446"))
INTERVAL_SECONDS = float(os.getenv("CO2_EXPORTER_INTERVAL", "2"))
RETRY_DELAY_SECONDS = float(os.getenv("CO2_EXPORTER_RETRY_DELAY", "5"))

# Data validation constants
MIN_DATA_LENGTH = 5
END_BYTE = 0x0D
OP_CO2 = 0x50
OP_TEMPERATURE = 0x42


def open_device() -> hid.device | None:
    """Open and unlock the CO2 sensor device."""
    h = hid.device()
    try:
        logging.info("Attempting to connect to CO2 sensor...")
        h.open(VID, PID)
        h.send_feature_report([0x00] + MAGIC_KEY)
        time.sleep(0.5)
        logging.info("Device unlocked. Monitoring started...")
        return h
    except OSError as e:
        logging.error(f"Failed to open device: {e}")
        logging.info(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
        time.sleep(RETRY_DELAY_SECONDS)
        return None


def process_data(data: list[int]) -> None:
    """Process sensor data and update metrics."""
    if len(data) < MIN_DATA_LENGTH:
        return

    # Checksum verification
    if (data[0] + data[1] + data[2]) & 0xFF != data[3]:
        return

    # End byte verification
    if data[4] != END_BYTE:
        return

    op = data[0]
    val = (data[1] << 8) | data[2]

    if op == OP_CO2:
        CO2_LEVEL.set(val)
        logging.info(f"CO2: {val} ppm")
    elif op == OP_TEMPERATURE:
        temp_c = val / 16.0 - 273.15
        TEMP_LEVEL.set(temp_c)
        logging.info(f"Temp: {temp_c:.2f} °C")


def monitor() -> None:
    """Monitor CO2 sensor and update metrics."""
    while True:
        h = open_device()
        if h is None:
            continue

        try:
            while True:
                data = h.read(8, timeout_ms=1000)
                if data:
                    process_data(data)
                time.sleep(INTERVAL_SECONDS)
        except Exception:
            logging.exception("Error during monitoring")
            time.sleep(RETRY_DELAY_SECONDS)
        finally:
            h.close()


def main() -> None:
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    start_http_server(EXPORTER_PORT)
    logging.info(f"Exporter listening on port {EXPORTER_PORT}")
    logging.info(f"Polling interval: {INTERVAL_SECONDS}s")
    monitor()


if __name__ == "__main__":
    main()
