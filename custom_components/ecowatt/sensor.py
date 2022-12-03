"""Support for Ecowatt sensor."""

import logging
from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, COORDINATOR_ECOWATT, MANUFACTURER, MODEL

_LOGGER = logging.getLogger(__name__)

ALERT_COLOR_LIST_FR = [None, "Vert", "Orange", "Rouge"]

@dataclass
class EcowattSensorEntityDescription(SensorEntityDescription):
  day: int = 0

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Ecowatt sensor platform."""
    coordinator_ecowatt = hass.data[DOMAIN][entry.entry_id][COORDINATOR_ECOWATT]

    entities = [
      EcowattSensor(coordinator_ecowatt, EcowattSensorEntityDescription(
        key="status_today",
        name="Ecowatt Aujourd'hui",
        day=0,
      )),
      EcowattSensor(coordinator_ecowatt, EcowattSensorEntityDescription(
        key="status_tomorrow",
        name="Ecowatt Demain",
        day=1,
      )),
       EcowattSensor(coordinator_ecowatt, EcowattSensorEntityDescription(
        key="status_j2",
        name="Ecowatt J+2",
        day=2,
      )),
      EcowattSensor(coordinator_ecowatt, EcowattSensorEntityDescription(
        key="status_j3",
        name="Ecowatt J+3",
        day=3,
      ))
    ]

    async_add_entities(entities, False)


class EcowattSensor(CoordinatorEntity, SensorEntity):
  """Representation of a Ecowatt sensor."""
  
  def __init__(
      self,
      coordinator: DataUpdateCoordinator,
      description: EcowattSensorEntityDescription,
  ) -> None:
      """Initialize the Ecowatt sensor."""
      super().__init__(coordinator)
      self.entity_id = f"sensor.ecowatt_day_{description.day}"
      self.entity_description = description
      self._day = description.day
      self._attr_unique_id = f"day_{description.day}"

  @property
  def device_info(self) -> DeviceInfo:
      """Return the device info."""
      return DeviceInfo(
          entry_type=DeviceEntryType.SERVICE,
          identifiers={(DOMAIN, "api")},
          manufacturer=MANUFACTURER,
          model=MODEL,
          name=self.coordinator.name,
      )

  @property
  def native_value(self):
      """Return the state."""
      if not self.coordinator.data.get("error"):
          today = list(self.coordinator.data.values())[0]
          _LOGGER.debug(
            "Get native value %s",
            today,
          )
          return ALERT_COLOR_LIST_FR[today['dvalue']]


      return "unknown"

  @property
  def extra_state_attributes(self):
      """Return the state attributes."""
      if not self.coordinator.data.get("error"):
          signals = list(self.coordinator.data.values())
          data = signals[self._day]
          
          attrs = {
            "generation_date": data['GenerationFichier'],
            "message": data['message'],
          }

          for value in list(data['values']):
            attrs[f"h{value['pas']}"] = ALERT_COLOR_LIST_FR[value['hvalue']]

          return attrs
      
      return {}