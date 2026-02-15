# win-co2-exporter

A background service to read CO2-mini sensor values and export them (e.g., for Prometheus).

## Prerequisites

- **OS**: Windows 10 / 11 (x64)
- **Hardware**: CO2-mini (NDIR CO2 Sensor)
- **Privileges**: Administrator rights (required for service registration and event log creation)

## Setup Instructions

### 1. Install uv

`uv` is used for Python environment management.
Refer to the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) to set up `uv` on your system.

### 2. Install servy-cli

`servy` is a Windows service wrapper.
Refer to the [official servy installation guide](https://github.com/aelassas/servy#getting-started) to install the tool. Ensure `servy-cli.exe` is available in your system PATH.

### 3. Clone the Repository

Clone this project to a generic directory.

```powershell
git clone https://github.com/kui/win-co2-exporter.git C:\tools\win-co2-exporter
cd C:\tools\win-co2-exporter
```

### 4. Install the Service

Run the following command in an **Administrator PowerShell** to register the script as a Windows service.

```powershell
servy-cli install `
  --name "CO2Exporter" `
  --path "%USERPROFILE%\.local\bin\uv.exe" `
  --params "run C:\tools\win-co2-exporter\co2_exporter.py" `
  --startupDir "C:\tools\win-co2-exporter" `
  --startupType Automatic `
  --stdout "C:\tools\win-co2-exporter\stdout.log" `
  --stderr "C:\tools\win-co2-exporter\stderr.log"
```

## Configuration

The exporter can be configured via environment variables:

- `CO2_EXPORTER_PORT`: HTTP server port (default: 4446)
- `CO2_EXPORTER_INTERVAL`: Polling interval in seconds (default: 2)
- `CO2_EXPORTER_RETRY_DELAY`: Retry delay after connection failure in seconds (default: 5)

## Service Management

| Action        | Command                                    |
| :------------ | :----------------------------------------- |
| **Start**     | `servy-cli start --name "CO2Exporter"`     |
| **Stop**      | `servy-cli stop --name "CO2Exporter"`      |
| **Status**    | `servy-cli status --name "CO2Exporter"`    |
| **Uninstall** | `servy-cli uninstall --name "CO2Exporter"` |

## Verification

To verify the exporter is running and exposing metrics:

```powershell
curl http://localhost:4446/metrics
```

Expected output includes metrics like:

```
# HELP co2mini_co2_ppm CO2 concentration in ppm
# TYPE co2mini_co2_ppm gauge
co2mini_co2_ppm 650.0
# HELP co2mini_temperature_celsius Temperature in Celsius
# TYPE co2mini_temperature_celsius gauge
co2mini_temperature_celsius 23.5
```

## Troubleshooting & Logs

If the service fails to start, refer to the following logs for details:

- `C:\tools\win-co2-exporter\stdout.log`
- `C:\tools\win-co2-exporter\stderr.log`

Common errors such as "Failed to ensure Event Log source" indicate that the command was not executed with Administrator privileges.
