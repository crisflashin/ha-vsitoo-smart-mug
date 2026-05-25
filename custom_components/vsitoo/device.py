import asyncio
import logging
from bleak import BleakClient
from bleak_retry_connector import establish_connection, BleakClientWithServiceCache
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import (
    VSITOO_CHAR_NOTIFY_UUID,
    VSITOO_CHAR_WRITE_UUID,
    CMD_INIT,
    CMD_PING,
    IDX_BATTERY,
    IDX_CURRENT_TEMP,
    IDX_TARGET_TEMP,
)

_LOGGER = logging.getLogger(__name__)

class VsitooDevice:
    def __init__(self, hass: HomeAssistant, address: str):
        self.hass = hass
        self.address = address
        self._client = None
        self._callbacks = []
        self._ping_task = None
        self._is_connected = False
        self.battery = None
        self.battery_voltage = None
        self.tdv = None
        self.current_temp = None
        self.target_temp = None
        self.mode = None
        self.is_charging = False

    def register_callback(self, callback):
        self._callbacks.append(callback)

    def _notify_callbacks(self):
        for callback in self._callbacks:
            callback()

    async def connect(self):
        ble_device = bluetooth.async_ble_device_from_address(self.hass, self.address, connectable=True)
        if not ble_device:
            _LOGGER.error("Dispositivo BLE no encontrado en el escaneo de HA. Asegúrate de que el vaso esté libre y cerca del proxy.")
            return False

        try:
            self._client = await establish_connection(
                client_class=BleakClientWithServiceCache,
                device=ble_device,
                name=self.address,
                disconnected_callback=self._handle_disconnect,
                max_attempts=3
            )
            self._is_connected = True
            _LOGGER.info("Conectado al vaso VSITOO %s", self.address)
            
            await self._client.start_notify(VSITOO_CHAR_NOTIFY_UUID, self._notification_handler)
            await self._client.write_gatt_char(VSITOO_CHAR_WRITE_UUID, CMD_INIT, response=False)
            
            self._ping_task = asyncio.create_task(self._ping_loop())
            return True
        except Exception as e:
            _LOGGER.error("Error conectando a VSITOO: %s", e)
            self._is_connected = False
            return False

    def _handle_disconnect(self, client):
        _LOGGER.warning("Desconectado de VSITOO %s", self.address)
        self._is_connected = False
        if self._ping_task:
            self._ping_task.cancel()

    async def _ping_loop(self):
        while self._is_connected:
            try:
                await self._client.write_gatt_char(VSITOO_CHAR_WRITE_UUID, CMD_PING, response=False)
            except Exception as e:
                _LOGGER.error("Error enviando ping: %s", e)
                break
            await asyncio.sleep(2)

    def _notification_handler(self, sender, data):
        if len(data) >= 18:
            state = data[2] # Byte 2 = Estado (00=Idle, 02=Heating, 03=Charging)
            self.is_charging = (state == 3)
            
            self.battery = data[6] # Byte 6 es la Batería (confirmado)
            self.current_temp = data[3] # Byte 3 es la Temperatura Actual (confirmado)
            
            # Voltajes extraídos en milivoltios
            self.tdv = int.from_bytes(data[14:16], byteorder='big')
            self.battery_voltage = int.from_bytes(data[16:18], byteorder='big')
            
            self.mode = data[5] # Byte 5 es el Modo de Calentamiento (0=Off, 1, 2, 3)
            if self.mode == 1:
                self.target_temp = data[8] # Byte 8 es el Target del modo Warm
            elif self.mode == 2:
                self.target_temp = data[7] # Byte 7 es el Target del modo Hot
            elif self.mode == 3:
                self.target_temp = data[9] # Byte 9 es el Target del modo Steaming
            else:
                self.target_temp = data[7] # Default fallback
            
            self._notify_callbacks()

    async def set_target_temperature(self, temp: int):
        if self._is_connected:
            # Escribimos la temperatura en el modo Hot (0x02) y lo activamos
            cmd1 = bytearray([0x04, 0x02, temp, 0x00])
            cmd2 = bytearray([0x05, 0x02])
            try:
                await self._client.write_gatt_char(VSITOO_CHAR_WRITE_UUID, cmd1, response=False)
                await asyncio.sleep(0.2)
                await self._client.write_gatt_char(VSITOO_CHAR_WRITE_UUID, cmd2, response=False)
            except Exception as e:
                _LOGGER.error("Error seteando temperatura: %s", e)

    async def turn_off(self):
        if self._is_connected:
            cmd = bytearray([0x05, 0x00]) # 00 = Off
            try:
                await self._client.write_gatt_char(VSITOO_CHAR_WRITE_UUID, cmd, response=False)
            except Exception as e:
                _LOGGER.error("Error apagando vaso: %s", e)

    async def disconnect(self):
        if self._ping_task:
            self._ping_task.cancel()
        if self._client and self._client.is_connected:
            await self._client.disconnect()
        self._is_connected = False
