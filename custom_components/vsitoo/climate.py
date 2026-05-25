"""Climate platform for VSITOO."""
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.const import UnitOfTemperature
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    device = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([VsitooClimate(device)])

class VsitooClimate(ClimateEntity):
    _attr_name = "Calentador VSITOO"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_target_temperature_step = 1
    _attr_min_temp = 44
    _attr_max_temp = 66

    def __init__(self, device):
        self.device = device
        self._attr_unique_id = f"{device.address}_climate"

    async def async_added_to_hass(self):
        self.device.register_callback(self.async_write_ha_state)

    @property
    def hvac_mode(self):
        return HVACMode.OFF if self.device.mode == 0 else HVACMode.HEAT

    @property
    def current_temperature(self):
        return self.device.current_temp

    @property
    def target_temperature(self):
        return self.device.target_temp

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get("temperature")
        if temp is not None:
            await self.device.set_target_temperature(int(temp))

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVACMode.OFF:
            await self.device.turn_off()
        elif hvac_mode == HVACMode.HEAT:
            await self.device.set_target_temperature(self.device.target_temp or 54)
