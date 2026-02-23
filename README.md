<a href="https://www.flaticon.com/free-icon/smart-fridge_2274715" target="_blank">
   <img width="150" align="right" src="./resources/smart-fridge.png"></img>
</a>

# Fridge Smart Plug Power Controller

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.13.7+](https://img.shields.io/badge/python-3.13.7+-blue.svg)](https://www.python.org/downloads/release/python-3137/)
![Python tests](https://github.com/AleksaMCode/fridge-smart-plug-power-controller/actions/workflows/tests.yml/badge.svg?branch=master)

A Python microservice that automatically controls an outdoor fridge based on ambient temperature. It turns the fridge ON when it's warm enough to need cooling, and turns it OFF when it's too cold; protecting both the appliance and the food inside.

## The Problem

I keep a fridge on my terrace for weekly meal prep, but standard fridges aren't designed to operate in temperatures below $10 \degree \text{C}$. During winter, outdoor temperatures fluctuate: leaving the fridge off risks food spoilage when daytime temperatures rise above $10 \degree \text{C}$, while leaving it on in very cold conditions could damage the compressor and other components.

## The Solution

This service connects to a **Tapo smart plug** ([P110](https://www.tapo.com/en/product/smart-plug/tapo-p110/)) and monitors outdoor temperature via the [**OpenWeatherMap API**](https://openweathermap.org/api). When the temperature rises above a safe threshold, it turns the fridge on. When it drops back below the threshold, it turns the fridge off. The fridge runs only when needed, reducing the risk of damage even though I’m operating it under suboptimal conditions (around $5 \degree \text{C}$).

### How It Works

- **Temperature above threshold** (default: $≥5 \degree \text{C}$) → plug turns **on**, fridge runs
- **Temperature below threshold - delta** (default: $≤3 \degree \text{C}$) → plug turns **off**, fridge stops
- **Temperature in between** ($3–5 \degree \text{C}$ by default) → **idle**, no change (prevents rapid switching)

A configurable hysteresis (`TEMPERATURE_DELTA`) avoids rapid on/off cycling when the temperature hovers near the threshold.

## Requirements

- Python 3.13
- A **Tapo P110** smart plug (or compatible Tapo device)
- An **OpenWeatherMap** API key (free tier available)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fridge-smart-plug-power-controller
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copy the settings template and configure:
   ```bash
   cp settings.template settings.py
   ```
   Edit `settings.py` with your credentials and preferences.

## Configuration

Edit `settings.py` with your own values:

| Variable | Description |
|----------|-------------|
| `TAPO_EMAIL` | Your Tapo account email |
| `TAPO_PASSWORD` | Your Tapo account password |
| `TAPO_PLUG_IP` | Local static IP address of the smart plug |
| `OWM_API_KEY` | Your OpenWeatherMap API key |
| `OWM_LOCATION` | Location string for weather (e.g. `"Paris, FR"`) |
| `TEMPERATURE_THRESHOLD` | Temperature ($\degree \text{C}$) above which fridge turns on (default: $5.0$) |
| `TEMPERATURE_DELTA` | Hysteresis in $\degree \text{C}$; fridge turns off when $temp ≤ threshold - delta$ (default: $2.0$) |
| `CONTROLLER_TIMEOUT` | Seconds between temperature checks (default: $600$ = $10$ minutes) |

## Usage

Run the controller:

```bash
python controller.py
```

Or use the provided script:

```bash
./start_controller.sh
```

The service runs continuously, checking the weather every $10$ minutes and adjusting the plug state accordingly. Logs are written to `logs/fsppc-info.log` and to the console.

## Running on System Startup (Cron)

To run the controller automatically when the system boots, add a cron job using `@reboot`:

1. Make the script executable (if not already):
   ```bash
   chmod +x start_controller.sh
   ```

2. Open the crontab for the user that will run the controller:
   ```bash
   crontab -e
   ```

3. Add this line (replace `/path/to/fridge-smart-plug-power-controller` with your actual project path):
   ```
   @reboot cd /path/to/fridge-smart-plug-power-controller && ./start_controller.sh >> logs/cron.log 2>&1 &
   ```

   The controller must be started from the project directory so the virtual environment and `settings.py` are found. The trailing `&` runs it in the background so cron does not block. Output is appended to `logs/cron.log` for debugging.

> [!NOTE]
>
> The controller will start once at boot and keep running. If you prefer automatic restarts on failure, consider a systemd service or process manager like `supervisord` instead.