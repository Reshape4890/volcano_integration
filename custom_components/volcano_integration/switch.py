"""switch.py - Volcano Integration for Home Assistant."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory  # For Diagnostics
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Volcano switch entities for a config entry."""
    _LOGGER.debug("Setting up Volcano switches for entry: %s", entry.entry_id)

    manager = hass.data[DOMAIN][entry.entry_id]

    entities = [
        VolcanoVibrationSwitch(manager, entry),
        VolcanoDisplayOffOnCoolSwitch(manager, entry),
    ]
    async_add_entities(entities)


class VolcanoVibrationSwitch(SwitchEntity):
    """Switch entity for the Volcano's Vibration setting."""

    def __init__(self, manager, config_entry):
        super().__init__()
        self._manager = manager
        self._config_entry = config_entry
        self._attr_name = "Volcano Vibration"
        self._attr_unique_id = f"volcano_vibration_{self._manager.bt_address}"
        self._attr_icon = "mdi:vibrate"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._manager.bt_address)},
            "name": self._config_entry.data.get("device_name", "Volcano Vaporizer"),
            "manufacturer": "Storz & Bickel",
            "model": "Volcano Hybrid Vaporizer",
            "sw_version": "1.0.0",
            "via_device": None,
        }
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self):
        return bool(self._manager.vibration_enabled)

    @property
    def available(self):
        """Available only when Bluetooth is connected."""
        return self._manager.bt_status == "CONNECTED"

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug("User turned Vibration on")
        if not await self._manager.wait_for_write_ready():
            _LOGGER.warning("Vibration: no usable connection — write skipped.")
            raise HomeAssistantError("Volcano: set_vibration failed — connection not ready.")
        await self._manager.set_vibration(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug("User turned Vibration off")
        if not await self._manager.wait_for_write_ready():
            _LOGGER.warning("Vibration: no usable connection — write skipped.")
            raise HomeAssistantError("Volcano: set_vibration failed — connection not ready.")
        await self._manager.set_vibration(False)
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Register for state updates."""
        _LOGGER.debug("%s added to Home Assistant.", self._attr_name)
        self._manager.register_sensor(self)

    async def async_will_remove_from_hass(self):
        """Unregister to stop receiving updates."""
        _LOGGER.debug("%s removed from Home Assistant.", self._attr_name)
        self._manager.unregister_sensor(self)


class VolcanoDisplayOffOnCoolSwitch(SwitchEntity):
    """Switch entity for the Volcano's Display Off on Cooling setting."""

    def __init__(self, manager, config_entry):
        super().__init__()
        self._manager = manager
        self._config_entry = config_entry
        self._attr_name = "Volcano Display Off on Cooling"
        self._attr_unique_id = f"volcano_display_off_on_cool_{self._manager.bt_address}"
        self._attr_icon = "mdi:monitor-off"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._manager.bt_address)},
            "name": self._config_entry.data.get("device_name", "Volcano Vaporizer"),
            "manufacturer": "Storz & Bickel",
            "model": "Volcano Hybrid Vaporizer",
            "sw_version": "1.0.0",
            "via_device": None,
        }
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self):
        return bool(self._manager.display_off_on_cool)

    @property
    def available(self):
        """Available only when Bluetooth is connected."""
        return self._manager.bt_status == "CONNECTED"

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug("User turned Display Off on Cooling on")
        if not await self._manager.wait_for_write_ready():
            _LOGGER.warning("Display Off on Cooling: no usable connection — write skipped.")
            raise HomeAssistantError("Volcano: set_display_off_on_cool failed — connection not ready.")
        await self._manager.set_display_off_on_cool(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug("User turned Display Off on Cooling off")
        if not await self._manager.wait_for_write_ready():
            _LOGGER.warning("Display Off on Cooling: no usable connection — write skipped.")
            raise HomeAssistantError("Volcano: set_display_off_on_cool failed — connection not ready.")
        await self._manager.set_display_off_on_cool(False)
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Register for state updates."""
        _LOGGER.debug("%s added to Home Assistant.", self._attr_name)
        self._manager.register_sensor(self)

    async def async_will_remove_from_hass(self):
        """Unregister to stop receiving updates."""
        _LOGGER.debug("%s removed from Home Assistant.", self._attr_name)
        self._manager.unregister_sensor(self)
