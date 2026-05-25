"""Sensor platform for VSITOO."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfElectricPotential
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    device = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        VsitooBatterySensor(device), 
        VsitooTemperatureSensor(device),
        VsitooBatteryVoltageSensor(device),
        VsitooTDVSensor(device)
    ])

class VsitooBatterySensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_name = "Batería VSITOO"
    _attr_icon = "mdi:battery-bluetooth"

    def __init__(self, device):
        self.device = device
        self._attr_unique_id = f"{device.address}_battery"

    async def async_added_to_hass(self):
        self.device.register_callback(self.async_write_ha_state)

    @property
    def native_value(self):
        return self.device.battery

class VsitooTemperatureSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_name = "Temperatura Actual VSITOO"
    _attr_icon = "mdi:cup-water"

    def __init__(self, device):
        self.device = device
        self._attr_unique_id = f"{device.address}_current_temp"

    async def async_added_to_hass(self):
        self.device.register_callback(self.async_write_ha_state)

    @property
    def native_value(self):
        return self.device.current_temp

class VsitooBatteryVoltageSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Voltaje Batería VSITOO"
    _attr_icon = "mdi:lightning-bolt"

    def __init__(self, device):
        self.device = device
        self._attr_unique_id = f"{device.address}_battery_voltage"

    async def async_added_to_hass(self):
        self.device.register_callback(self.async_write_ha_state)

    @property
    def native_value(self):
        return self.device.battery_voltage

class VsitooTDVSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Voltaje TDV VSITOO"
    _attr_icon = "mdi:lightning-bolt-circle"

    def __init__(self, device):
        self.device = device
        self._attr_unique_id = f"{device.address}_tdv"

    async def async_added_to_hass(self):
        self.device.register_callback(self.async_write_ha_state)

    @property
    def native_value(self):
        return self.device.tdv
