"""Offline integration exercising the central payload test contract with real HA."""

import voluptuous as vol
import yaml
from homeassistant.helpers import config_validation as cv

DOMAIN = "payload_sample"
SCHEMA = vol.Schema(
    {
        vol.Required("payload"): list,
        vol.Required("width"): cv.positive_int,
        vol.Required("height"): cv.positive_int,
        vol.Optional("entity_id"): cv.entity_ids,
    }
)


async def async_setup(hass, config):
    return True


async def async_setup_entry(hass, entry):
    hass.services.async_register(DOMAIN, "draw", send_device, schema=SCHEMA)
    string_schema = vol.Schema(
        {
            vol.Required("payload"): str,
            vol.Required("width"): cv.positive_int,
            vol.Required("height"): cv.positive_int,
            vol.Optional("entity_id"): cv.entity_ids,
        }
    )
    hass.services.async_register(DOMAIN, "draw_yaml", send_device, schema=string_schema)
    return True


async def async_unload_entry(hass, entry):
    hass.services.async_remove(DOMAIN, "draw")
    hass.services.async_remove(DOMAIN, "draw_yaml")
    return True


async def send_device(call):
    raise AssertionError("Documentation validation must never send a device command")


def render_image(payload, context, width, height):
    import imagespec

    return imagespec.render(payload, context=context, width=width, height=height)


def parse_payload(value):
    return yaml.safe_load(value)


def render_yaml_image(value, context, width, height):
    return render_image(parse_payload(value), context, width, height)
