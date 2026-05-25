"""Binary sensor platform for VSITOO."""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    device = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([VsitooChargingSensor(device)])

class VsitooChargingSensor(BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
    _attr_name = "Cargando VSITOO"

    def __init__(self, device):
        self.device = device
        self._attr_unique_id = f"{device.address}_charging"

    async def async_added_to_hass(self):
        self.device.register_callback(self.async_write_ha_state)

    @property
    def is_on(self):
        return self.device.is_charging
