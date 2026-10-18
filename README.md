<a href="https://www.flaticon.com/free-icon/smart-fridge_2274715" target="_blank">
   <img width="150" align="right" src="./resources/smart-fridge.png"></img>
</a>

# Fridge Smart Plug Power Controller

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.13.7+](https://img.shields.io/badge/python-3.13.7+-blue.svg)](https://www.python.org/downloads/release/python-3137/)
![](https://img.shields.io/github/v/release/AleksaMCode/fridge-smart-plug-power-controller)
![Python tests](https://github.com/AleksaMCode/fridge-smart-plug-power-controller/actions/workflows/tests.yml/badge.svg?branch=master)

A Python microservice that automatically controls an outdoor fridge based on ambient temperature. It turns the fridge ON when it's warm enough to need cooling, and turns it OFF when it's too cold; protecting both the appliance and the food inside.

<p align="center">
<img
src="./resources/controller.svg?raw=true"
alt="Controller overview"
width="70%"
class="center"
/>
<p align="center">
    <label><b>Fig. 1</b>: Controller <code>0.3.0</code> system overview</label>
    </p>
</p>


## The Problem

I keep a fridge on my terrace for weekly meal prep, but standard fridges aren't designed to operate in temperatures below $10 \degree \text{C}$. During winter, outdoor temperatures fluctuate: leaving the fridge off risks food spoilage when daytime temperatures rise above $10 \degree \text{C}$, while leaving it on in very cold conditions could damage the compressor and other components.

## The Solution

This service connects to a **Tapo smart plug** ([P110](https://www.tapo.com/en/product/smart-plug/tapo-p110/)) and monitors outdoor temperature via either:

- Local **[Tapo T310](https://www.tp-link.com/us/smart-home/smart-sensor/tapo-t310/)** temperature sensor through **[Tapo H100](https://www.tp-link.com/us/home-networking/smart-hub/tapo-h100/)** hub, or
- [**OpenWeatherMap API**](https://openweathermap.org/api).

When the temperature rises above a safe threshold, it turns the fridge on. When it drops back below the threshold, it turns the fridge off. The fridge runs only when needed, reducing the risk of damage even though I’m operating it under suboptimal conditions (around $5 \degree \text{C}$).

### How It Works

| Description | Default Temperature | Action |
|---|---|---|
| Temperature above threshold | $≥5 \degree \text{C}$ | Plug turns **ON** (fridge runs) |
| Temperature below threshold - delta | $≤3 \degree \text{C}$ | Plug turns **OFF** (fridge stops) |
| Temperature in between (hysteresis window) | $3–5 \degree \text{C}$ | **Idle** (no change, prevents rapid switching) |

> [!NOTE] 
> A configurable hysteresis (`TEMPERATURE_DELTA`) avoids rapid on/off cycling when the temperature hovers near the threshold.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AleksaMCode/fridge-smart-plug-power-controller.gits
   cd fridge-smart-plug-power-controller
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copy the environment template and configure:
   ```bash
   cp .env.template .env
   ```
   Edit `.env` with your credentials and preferences.

## Usage

Run the controller:

```bash
python main.py
```

The service runs continuously, checking temperature every N minutes and adjusting the plug state accordingly. Logs are written to `logs/fsppc-info.log` and to the console.

## Docker Deployment

Run the service with Docker Compose:

```bash
docker compose up -d --build
```

The compose setup expects a local `.env` file in the project root.