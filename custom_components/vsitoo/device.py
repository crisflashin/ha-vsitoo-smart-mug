"""Bluetooth transport and state handling for VSITOO smart mugs."""
from __future__ import annotations

import asyncio
import logging

from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import CMD_INIT, CMD_PING, VSITOO_CHAR_NOTIFY_UUID, VSITOO_CHAR_WRITE_UUID

_LOGGER = logging.getLogger(__name__)


class VsitooDevice:
    """Maintain a resilient BLE connection to a VSITOO mug."""

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        self.hass = hass
        self.address = address.upper()
        self._client = None
        self._callbacks: list = []
        self._manager_task: asyncio.Task | None = None
        self._ping_task: asyncio.Task | None = None
        self._connect_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()
        self._reconnect_event = asyncio.Event()
        self._stopped = True
        self._is_connected = False
        self._missing_logged = False

        self.battery = None
        self.battery_voltage = None
        self.tdv = None
        self.current_temp = None
        self.target_temp = None
        self.mode = None
        self.is_charging = False

    @property
    def available(self) -> bool:
        return self._is_connected and self._client is not None

    def register_callback(self, callback):
        self._callbacks.append(callback)

        def remove_callback() -> None:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

        return remove_callback

    def _notify_callbacks(self) -> None:
        for callback in list(self._callbacks):
            callback()

    async def async_start(self) -> None:
        """Start the background connection manager without blocking HA startup."""
        if self._manager_task and not self._manager_task.done():
            return
        self._stopped = False
        # This is a permanent reconnect loop, not startup work.  Registering it
        # with async_create_task makes Home Assistant wait for an infinite task
        # during "Wrapping up startup".
        self._manager_task = self.hass.async_create_background_task(
            self._connection_manager(), f"vsitoo_connection_{self.address}"
        )

    async def _connection_manager(self) -> None:
        """Reconnect whenever the mug starts advertising or a link is lost."""
        retry_delay = 1
        while not self._stopped:
            if not self.available:
                connected = await self._connect_once()
                retry_delay = 5 if connected else min(max(retry_delay * 2, 10), 60)
            else:
                retry_delay = 60

            self._reconnect_event.clear()
            try:
                await asyncio.wait_for(self._reconnect_event.wait(), timeout=retry_delay)
            except TimeoutError:
                pass
            except asyncio.CancelledError:
                return

    async def _connect_once(self) -> bool:
        if self._stopped or self.available:
            return self.available

        async with self._connect_lock:
            if self._stopped or self.available:
                return self.available

            ble_device = bluetooth.async_ble_device_from_address(
                self.hass, self.address, connectable=True
            )
            if not ble_device:
                if not self._missing_logged:
                    _LOGGER.warning(
                        "VSITOO %s no aparece todavía en el escaneo BLE; "
                        "se seguirá intentando automáticamente",
                        self.address,
                    )
                    self._missing_logged = True
                return False

            try:
                client = await establish_connection(
                    client_class=BleakClientWithServiceCache,
                    device=ble_device,
                    name=f"VSITOO {self.address}",
                    disconnected_callback=self._handle_disconnect,
                    max_attempts=3,
                )
                await client.start_notify(
                    VSITOO_CHAR_NOTIFY_UUID, self._notification_handler
                )
                await client.write_gatt_char(
                    VSITOO_CHAR_WRITE_UUID, CMD_INIT, response=False
                )
            except asyncio.CancelledError:
                raise
            except Exception as err:
                _LOGGER.warning("No se pudo conectar a VSITOO %s: %s", self.address, err)
                self._is_connected = False
                self._client = None
                return False

            self._client = client
            self._is_connected = True
            self._missing_logged = False
            _LOGGER.info("Conectado al vaso VSITOO %s", self.address)
            self._notify_callbacks()
            # The keepalive loop is also intentionally long-lived.
            self._ping_task = self.hass.async_create_background_task(
                self._ping_loop(), f"vsitoo_ping_{self.address}"
            )
            return True

    def _handle_disconnect(self, client) -> None:
        if client is not self._client and self._client is not None:
            return
        was_connected = self._is_connected
        self._is_connected = False
        self._client = None
        if self._ping_task and not self._ping_task.done():
            self._ping_task.cancel()
        self._ping_task = None
        if was_connected:
            _LOGGER.warning(
                "Desconectado de VSITOO %s; intentando reconectar", self.address
            )
        self._notify_callbacks()
        if not self._stopped:
            self._reconnect_event.set()

    async def _ping_loop(self) -> None:
        try:
            while self.available and not self._stopped:
                await self._write(CMD_PING)
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            return
        except Exception as err:
            _LOGGER.warning("Falló el enlace con VSITOO %s: %s", self.address, err)
            client = self._client
            self._is_connected = False
            self._client = None
            self._notify_callbacks()
            self._reconnect_event.set()
            if client and client.is_connected:
                try:
                    await client.disconnect()
                except Exception:
                    pass

    async def _write(self, data: bytes | bytearray) -> None:
        client = self._client
        if not self.available or client is None:
            self._reconnect_event.set()
            raise HomeAssistantError(
                "El vaso VSITOO no está conectado por Bluetooth; se está reintentando"
            )
        async with self._write_lock:
            await client.write_gatt_char(
                VSITOO_CHAR_WRITE_UUID, data, response=False
            )

    def _notification_handler(self, sender, data: bytearray) -> None:
        if len(data) < 18:
            _LOGGER.debug("Paquete VSITOO corto ignorado: %s", data.hex())
            return

        state = data[2]
        self.is_charging = state == 3
        self.battery = data[6]
        self.current_temp = data[3]
        self.tdv = int.from_bytes(data[14:16], byteorder="big")
        self.battery_voltage = int.from_bytes(data[16:18], byteorder="big")
        self.mode = data[5]

        if self.mode == 1:
            self.target_temp = data[8]
        elif self.mode == 2:
            self.target_temp = data[7]
        elif self.mode == 3:
            self.target_temp = data[9]
        else:
            self.target_temp = data[7]

        self._notify_callbacks()

    async def set_target_temperature(self, temp: int) -> None:
        await self._write(bytearray([0x04, 0x02, temp, 0x00]))
        await asyncio.sleep(0.2)
        await self._write(bytearray([0x05, 0x02]))

    async def turn_off(self) -> None:
        await self._write(bytearray([0x05, 0x00]))

    async def async_stop(self) -> None:
        self._stopped = True
        self._reconnect_event.set()
        for task in (self._manager_task, self._ping_task):
            if task and not task.done():
                task.cancel()
        self._manager_task = None
        self._ping_task = None

        client = self._client
        self._client = None
        self._is_connected = False
        if client and client.is_connected:
            try:
                await client.disconnect()
            except Exception as err:
                _LOGGER.debug("Error cerrando VSITOO %s: %s", self.address, err)
        self._notify_callbacks()
