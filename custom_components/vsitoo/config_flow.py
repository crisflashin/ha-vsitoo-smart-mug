"""Config flow for VSITOO."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import async_discovered_service_info
from .const import DOMAIN

class VsitooConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=f"VSITOO ({user_input['address']})", data=user_input)

        # Buscar dispositivos Bluetooth descubiertos por los proxies de HA
        devices = async_discovered_service_info(self.hass)
        vsitoo_devices = {
            dev.address: f"{dev.name} ({dev.address})"
            for dev in devices if dev.name and "VSITOO" in dev.name
        }

        # Si encontramos dispositivos, mostramos un desplegable. Si no, un campo de texto libre.
        if vsitoo_devices:
            data_schema = vol.Schema({
                vol.Required("address"): vol.In(vsitoo_devices)
            })
        else:
            data_schema = vol.Schema({
                vol.Required("address"): str
            })

        return self.async_show_form(step_id="user", data_schema=data_schema)
