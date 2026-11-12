# VSITOO Smart Mug for Home Assistant

Monitor your drink temperature and control the mug's heater directly from Home Assistant over Bluetooth Low Energy (BLE).

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=crisflashin&repository=ha-vsitoo-smart-mug&category=integration)

[Español](README.es.md) · [Troubleshooting](#troubleshooting) · [Report an issue](https://github.com/crisflashin/ha-vsitoo-smart-mug/issues)

## What you can do

| Entity | What it shows or controls |
| --- | --- |
| Climate | Turn heating on or off and set a target from 44 to 66 °C in 1 °C steps |
| Drink temperature | Current temperature in °C |
| Battery | Remaining charge in % |
| Charging | Whether the mug is charging |
| Battery voltage and TDV voltage | Two separate sensors in mV |

Everything runs locally. Home Assistant loads the entities while the mug is out of range and reconnects automatically when it can reach the mug again. Entities show as unavailable while disconnected.

## Before you start

- Enable [Bluetooth in Home Assistant](https://www.home-assistant.io/integrations/bluetooth/). Use a local adapter or a proxy that supports **active BLE connections**, such as an ESPHome Bluetooth proxy.
- Wake the mug and keep it within range of the adapter or proxy. Disconnect it from the VSITOO phone app so Home Assistant can connect.

## Install

### HACS

1. Select **Open in HACS** above. You can also open **HACS → ⋮ → Custom repositories**, add `https://github.com/crisflashin/ha-vsitoo-smart-mug` and select **Integration**.
2. Open **VSITOO Smart Mug** in HACS and select **Download**.
3. Restart Home Assistant.

### Manual installation

Copy [`custom_components/vsitoo`](custom_components/vsitoo/) into your Home Assistant configuration directory. The manifest should be at `config/custom_components/vsitoo/manifest.json`. Restart Home Assistant.

## Add the mug

1. Go to **Settings → Devices & services → Add integration** and search for **VSITOO Smart Mug**.
2. Pick the mug from the list of visible VSITOO devices. If the form shows a text field, enter the mug's Bluetooth MAC address.
3. Open the integration entry to see its entities. To control the mug from a dashboard, add a **Thermostat** card and select the VSITOO climate entity.

If you're upgrading an existing installation, update the files through HACS or replace them manually, then restart Home Assistant.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| The mug doesn't appear in the setup list | Wake it, move it closer to the adapter or proxy, and reopen the setup form. If you see a text field, enter the MAC address. |
| Entities stay unavailable | Disconnect the phone app and check that Home Assistant Bluetooth sees the mug through an adapter or proxy with active connections. The integration retries in the background. |
| The integration doesn't appear under Add integration | Confirm the download or check the manifest path, then restart Home Assistant. |

If the problem persists, open [an issue](https://github.com/crisflashin/ha-vsitoo-smart-mug/issues/new) with the mug model, Home Assistant version, Bluetooth adapter or proxy type, and relevant entries from **Settings → System → Logs**. Remove Bluetooth addresses and other private details before sharing logs.

This is an independent integration based on the mug's BLE protocol. Compatibility can vary by model and firmware.
