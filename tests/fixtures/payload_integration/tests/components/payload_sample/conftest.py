"""Load actual HA and use the example integration's real action and renderer."""

from functools import partial
from pathlib import Path

import pytest
from custom_components.payload_sample import parse_payload, render_image, render_yaml_image
from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
async def payload_example_setup(hass, enable_custom_integrations):
    hass.config.config_dir = str(Path(__file__).resolve().parents[3])
    entry = MockConfigEntry(domain="payload_sample", title="Offline payload device", data={})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set("sensor.payload_sample", "7")
    yield entry
    assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.fixture
def payload_example_adapter():
    def prepare(hass, example, normalized, data):
        from hass_standards_payload import PreparedPayload
        from imagespec import RenderContext

        context = RenderContext(palette="bw")
        options = {"width": data["width"], "height": data["height"]}
        if example.get("payload_format") == "yaml":
            return PreparedPayload(
                parse_payload(data["payload"]),
                context,
                options,
                partial(render_yaml_image, data["payload"], context, **options),
            )
        return PreparedPayload(
            data["payload"],
            context,
            options,
            partial(render_image, data["payload"], context, **options),
        )

    return prepare
