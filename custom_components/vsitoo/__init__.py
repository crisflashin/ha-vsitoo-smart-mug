"""The VSITOO integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .device import VsitooDevice

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "climate", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    address = entry.data["address"]
    
    device = VsitooDevice(hass, address)
    success = await device.connect()
    if not success:
        _LOGGER.error("No se pudo establecer la conexión inicial con el vaso VSITOO.")
        # Retornamos False para que HA lo vuelva a intentar más tarde.
        return False
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = device

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        device = hass.data[DOMAIN].pop(entry.entry_id)
        await device.disconnect()
    return unload_ok
