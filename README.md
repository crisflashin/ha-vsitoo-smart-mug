# VSITOO Smart Mug Custom Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=crisflashin&repository=ha-vsitoo-smart-mug&category=integration)

This is a custom integration for Home Assistant that allows you to natively connect and control your VSITOO Smart Mug via Bluetooth (BLE) using Home Assistant's Bluetooth proxies.

## Features
- **Live Liquid Temperature** (Celsius)
- **Real-time Battery %**
- **Charging State Detection** (Binary sensor)
- **Battery & TDV Voltage** in mV
- **Climate Entity (Thermostat)** to set your desired target temperature and turn the mug's heating on/off directly from Home Assistant.

## Installation via HACS (Recommended)
1. Open Home Assistant and go to **HACS**.
2. Click on **Integrations**.
3. Click the 3 dots in the top right corner and select **Custom repositories**.
4. Paste the URL of this repository (`https://github.com/crisflashin/ha-vsitoo-smart-mug`), select `Integration` as the category, and click **Add**.
5. Search for "VSITOO Smart Mug" in HACS, click Download, and **Restart Home Assistant**.

## Configuration
1. After restarting Home Assistant, go to **Settings -> Devices & Services**.
2. Click **Add Integration** and search for `VSITOO`.
3. If you have Bluetooth Proxies set up (like an ESP32), the mug should be automatically discovered.
4. Otherwise, you can enter your mug's MAC address manually.

> **Note**: The mug can only be connected to ONE device at a time. If it is connected to the official mobile app, Home Assistant will not be able to connect to it (and vice versa).

## Disclaimer
This integration was created by reverse-engineering the Bluetooth payload. It is not affiliated with the official VSITOO brand. Use at your own risk.
