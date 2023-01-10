from collections.abc import Callable
import logging

from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant

_LOGGER: logging.Logger = logging.getLogger(__package__)
from .const import *
from .device import HuaweiBottleMointor
from .entity import HuaweiBottleEntity


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: Callable
):
    """Configure platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device: HuaweiBottleMointor = coordinator.device
    sensors_data = device.sensors_data
    sensors = []
    for sensor_data in sensors_data:
        sensor_data = sensors_data[sensor_data]
        sensor = HuaweiSensor(coordinator, entry, sensor_data, ENTITY_ID_FORMAT)
        sensors.append(sensor)
        _LOGGER.error("Adding %s", sensor_data["name"])
    device.sensor_instances = sensors
    async_add_devices(sensors)


class HuaweiSensor(HuaweiBottleEntity):
    """imou sensor class."""

    _state = None

    @property
    def sensor_name(self) -> int:
        return self.sensor_instance["name"]

    @property
    def sensor_id(self) -> int:
        return self.sensor_instance["id"]

    @property
    def device_class(self) -> str:
        """Device device class."""
        if "battery" in self.sensor_instance["id"]:
            return "battery"

        if "waterintake" in self.sensor_instance["id"]:
            return "volume"

        if "humidity" in self.sensor_instance["id"]:
            return "humidity"
        if "temperature" in self.sensor_instance["id"]:
            return "temperature"
        return None

    @property
    def unit_of_measurement(self) -> str:
        """Provide unit of measurement."""
        if "battery" in self.sensor_instance["id"]:
            return "%"
        if "humidity" in self.sensor_instance["id"]:
            return "%"
        if "temperature" in self.sensor_instance["id"]:
            return "°C"
        if "waterintake" in self.sensor_instance["id"]:
            return "mL"
        return None

    @property
    def state(self):
        """Return the state of the sensor."""

        return self._state

    def set_state(self, stat):
        self._state = stat
