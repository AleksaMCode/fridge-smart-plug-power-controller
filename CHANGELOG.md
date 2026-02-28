# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-02-28

### Added

- Weather API error handling: temperature fetch is now wrapped in `try-catch`; the microservice continues running instead of crashing on fetch failure
- In-memory temperature cache (`temp`, `timestamp`) with 30-minute validity; when fetch fails, last known temperature is used if cache is fresh
- Safe mode: after 30 minutes without valid weather data, forces fridge ON (food safety first); normal operation resumes once data is available again

## [0.1.0] - 2026-02-23

### Added

- Initial release: Python microservice to control an outdoor fridge via Tapo smart plug based on OpenWeatherMap temperature
- Tapo P110 plug adapter with retry logic for device connections
- OpenWeatherMap weather adapter with retry logic for API calls
- Configurable temperature threshold and hysteresis delta to avoid rapid on/off cycling
- Controller loop checking temperature every 10 minutes and turning plug on/off accordingly
- `start_controller.sh` script for running the controller
- Cron-based startup instructions for running on system boot
