# Car Diagnosis Assistant

Windows desktop app for car fault diagnosis, OBD2 code lookup, service history, and MOT/tax tracking.

## Features

- **Diagnose** — enter vehicle details and symptoms to get ranked possible fault codes
- **Code Browser** — searchable OBD2 code list with severity, cost estimate, DIY/garage, causes, and repairs
- **OBD2 Adapter** — connect an ELM327 Bluetooth/serial adapter to read and clear live fault codes
- **Service History** — log services with date, mileage, garage, cost, and notes
- **MOT / Tax** — track MOT and tax expiry with status indicators: OK, DUE SOON, EXPIRED
- **Maintenance** — routine service intervals and estimated costs
- **History** — diagnosis log with CSV export
- **Reports** — export or print diagnosis reports

## Requirements

- Windows 10+
- Python 3.11+
- Optional: `pyserial` for live OBD2 adapter support

## Install

```powershell
git clone https://github.com/Jazblue/car-diagnostics.git
cd car-diagnostics
python -m pip install pyserial
python car_diagnosis.py
```

Or run the desktop shortcut: **Car Diagnosis**

## Usage

1. Open the app
2. Enter your vehicle in the **Diagnose** tab
3. Pick symptoms or type your own
4. Tap **Diagnose** to see likely codes
5. Double-click any code in **Code Browser** for full details
6. Use **OBD2 Adapter** to connect an ELM327 and read live codes
7. Save MOT/tax dates in **MOT / Tax**
8. Log services in **Service History**
9. Export or print reports from the diagnosis result

## Notes

- Local SQLite database stores history, service records, and MOT/tax reminders
- Vehicle details are saved automatically between sessions
- OBD2 adapter defaults to `COM3` at `38400` baud
