"""button.py - Volcano Integration for Home Assistant."""
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.exceptions import HomeAssistantError
from . import DOMAIN

from .const import (
    UUID_PUMP_ON,
    UUID_PUMP_OFF,
    UUID_HEAT_ON,
    UUID_HEAT_OFF,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Volcano buttons for a config entry."""
    _LOGGER.debug("Setting up Volcano buttons for entry: %s", entry.entry_id)

    manager = hass.data[DOMAIN][entry.entry_id]

    entities = [
        VolcanoConnectButton(manager, entry),
        VolcanoDisconnectButton(manager, entry),
        VolcanoPumpOnButton(manager, entry),
        VolcanoPumpOffButton(manager, entry),
        VolcanoHeatOnButton(manager, entry),
        VolcanoHeatOffButton(manager, entry),
    ]
    async_add_entities(entities)


class VolcanoBaseButton(ButtonEntity):
    """Base button for the Volcano integration that references the BT manager."""

    def __init__(self, manager, config_entry):
        super().__init__()
        self._manager = manager
        self._config_entry = config_entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._manager.bt_address)},
            "name": self._config_entry.data.get("device_name", "Volcano Vaporizer"),
            "manufacturer": "Storz & Bickel",
            "model": "Volcano Hybrid Vaporizer",
            "sw_version": "1.0.0",
            "via_device": None,
        }

    @property
    def available(self):
        """Default availability for buttons. Override in subclasses if needed."""
        return True

    async def async_added_to_hass(self):
        """Ensure state updates are triggered when the entity is added."""
        _LOGGER.debug("%s added to Home Assistant.", self._attr_name)
        self._manager.register_sensor(self)

    async def async_will_remove_from_hass(self):
        """Clean up when the entity is removed."""
        _LOGGER.debug("%s removed from Home Assistant.", self._attr_name)
        self._manager.unregister_sensor(self)


class VolcanoConnectButton(VolcanoBaseButton):
    """A button to force the Volcano integration to connect BLE."""

    def __init__(self, manager, config_entry):
        super().__init__(manager, config_entry)
        self._attr_name = "Volcano Connect"
        self._attr_unique_id = f"volcano_connect_button_{self._manager.bt_address}"
        self._attr_icon = "mdi:bluetooth-connect"

    async def async_press(self):
        """Handle button press."""
        _LOGGER.debug("VolcanoConnectButton pressed.")
        await self._manager.async_user_connect()


class VolcanoDisconnectButton(VolcanoBaseButton):
    """A button to force the Volcano integration to disconnect BLE."""

    def __init__(self, manager, config_entry):
        super().__init__(manager, config_entry)
        self._attr_name = "Volcano Disconnect"
        self._attr_unique_id = f"volcano_disconnect_button_{self._manager.bt_address}"
        self._attr_icon = "mdi:bluetooth-off"

    async def async_press(self):
        """Handle button press."""
        _LOGGER.debug("VolcanoDisconnectButton pressed.")
        await self._manager.async_user_disconnect()


class VolcanoPumpOnButton(VolcanoBaseButton):
    """A button to turn Pump ON by writing to a GATT characteristic."""

    def __init__(self, manager, config_entry):
        super().__init__(manager, config_entry)
        self._attr_name = "Volcano Pump On"
        self._attr_unique_id = f"volcano_pump_on_button_{self._manager.bt_address}"
        self._attr_icon = "mdi:air-purifier"

    @property
    def available(self):
        """Available only when Bluetooth is connected."""
        return self._manager.bt_status == "CONNECTED"

    async def async_press(self):
        """Handle button press."""
        _LOGGER.debug("VolcanoPumpOnButton pressed.")
        if not await self._manager.wait_for_write_ready():
            _LOGGER.warning("Pump On button: no usable connection — write skipped.")
            raise HomeAssistantError("Volcano: pump_on failed — connection not ready.")
        await self._manager.write_gatt_command(UUID_PUMP_ON, payload=b"\x01")


class VolcanoPumpOffButton(VolcanoBaseButton):
    """A button to turn Pump OFF by writing to a GATT characteristic."""

    def __init__(self, manager, config_entry):
        super().__init__(manager, config_entry)
        self._attr_name = "Volcano Pump Off"
        self._attr_unique_id = f"volcano_pump_off_button_{self._manager.bt_address}"
        self._attr_icon = "mdi:air-purifier-off"

    @property
    def available(self):
        """Available only when Bluetooth is connected."""
        return self._manager.bt_status == "CONNECTED"

    async def async_press(self):
        """Handle button press."""
        _LOGGER.debug("VolcanoPumpOffButton pressed.")
        if not await self._manager.wait_for_write_ready():
            _LOGGER.warning("Pump Off button: no usable connection — write skipped.")
            raise HomeAssistantError("Volcano: pump_off failed — connection not ready.")
        await self._manager.write_gatt_command(UUID_PUMP_OFF, payload=b"\x00")


class VolcanoHeatOnButton(VolcanoBaseButton):
    """A button to turn Heat ON by writing to a GATT characteristic."""

    def __init__(self, manager, config_entry):
        super().__init__(manager, config_entry)
        self._attr_name = "Volcano Heat On"
        self._attr_unique_id = f"volcano_heat_on_button_{self._manager.bt_address}"
        self._attr_icon = "mdi:fire"

    @property
    def available(self):
        """Available only when Bluetooth is connected."""
        return self._manager.bt_status == "CONNECTED"

    async def async_press(self):
        """Handle button press."""
        _LOGGER.debug("VolcanoHeatOnButton pressed.")
        if not await self._manager.wait_for_write_ready():
            _LOGGER.warning("Heat On button: no usable connection — write skipped.")
            raise HomeAssistantError("Volcano: heat_on failed — connection not ready.")
        await self._manager.write_gatt_command(UUID_HEAT_ON, payload=b"\x01")


class VolcanoHeatOffButton(VolcanoBaseButton):
    """A button to turn Heat OFF by writing to a GATT characteristic."""

    def __init__(self, manager, config_entry):
        super().__init__(manager, config_entry)
        self._attr_name = "Volcano Heat Off"
        self._attr_unique_id = f"volcano_heat_off_button_{self._manager.bt_address}"
        self._attr_icon = "mdi:fire-off"

    @property
    def available(self):
        """Available only when Bluetooth is connected."""
        return self._manager.bt_status == "CONNECTED"

    async def async_press(self):
        """Handle button press."""
        _LOGGER.debug("VolcanoHeatOffButton pressed.")
        if not await self._manager.wait_for_write_ready():
            _LOGGER.warning("Heat Off button: no usable connection — write skipped.")
            raise HomeAssistantError("Volcano: heat_off failed — connection not ready.")
        await self._manager.write_gatt_command(UUID_HEAT_OFF, payload=b"\x00")
