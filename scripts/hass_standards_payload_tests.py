"""Shipped contract tests executed by the central collector in the integration's scope."""

from __future__ import annotations

import copy
import inspect
from importlib.metadata import version

import pytest
import yaml
from hass_standards_payload import PreparedPayload, callable_origin, safe_path
from payload_documents import decoded_payload


@pytest.mark.asyncio
async def test_documented_payload(
    request, hass, payload_example_setup, payload_example_adapter, payload_example
):
    import imagespec
    from homeassistant.config_entries import ConfigEntryState
    from homeassistant.helpers import config_validation as cv
    from homeassistant.helpers import service as service_helper

    missing = [
        name for name in ("RenderContext", "render", "validate") if not hasattr(imagespec, name)
    ]
    assert not missing, (
        f"Installed imagespec {version('imagespec')} lacks required public APIs {missing}; preserve the declared minimum and resolve compatibility or record an explicitly approved exception"
    )
    RenderContext, render, validate = imagespec.RenderContext, imagespec.render, imagespec.validate
    from PIL import Image, ImageColor

    root = request.config._standards_payload_root
    domain = request.config._standards_payload_domain
    assert type(hass).__module__ == "homeassistant.core", "Use the real HA fixture"
    assert any(
        entry.state == ConfigEntryState.LOADED
        for entry in hass.config_entries.async_entries(domain)
    ), "Load the real integration entry before validating documented actions"
    action = yaml.safe_load(safe_path(root, payload_example["path"]).read_text())
    normalized = cv.SCRIPT_SCHEMA([copy.deepcopy(action)])[0]
    # HA's real preparation resolves action/target/data templates without calling
    # the service handler or sending a command to a device.
    call = service_helper.async_prepare_call_from_config(hass, normalized)
    service_domain, service_name = call["domain"], call["service"]
    data, target = call["service_data"], call["target"]
    if service_domain != domain:
        from homeassistant.helpers import entity_registry as er

        registry = er.async_get(hass)
        targets = target.get("entity_id", data.get("entity_id", []))
        if isinstance(targets, str):
            targets = [targets]
        entry_ids = {
            entry.entry_id
            for entry in hass.config_entries.async_entries(domain)
            if entry.state == ConfigEntryState.LOADED
        }
        assert any(
            (entity := registry.async_get(entity_id)) is not None
            and (entity.platform == domain or entity.config_entry_id in entry_ids)
            for entity_id in targets
        ), "A generic HA action must target an actual entity owned by this integration"
    registered = hass.services.async_services()[service_domain][service_name]
    assert registered.schema is not None, "The real registered action schema is required"
    assert callable_origin(registered.job.target).startswith(
        (f"custom_components.{domain}", "homeassistant.")
    ), "Do not replace the HA service with a test stub"
    schema_data = registered.schema({**data, **target})
    resolved_action = dict(normalized)
    resolved_action["data"] = schema_data
    if "data_template" in normalized:
        resolved_action["data_template"] = schema_data
    resolved_action["target"] = target
    resolved_payload = resolved_action
    for key in payload_example["payload_path"]:
        resolved_payload = resolved_payload[key]
    resolved_payload = decoded_payload(
        resolved_payload, payload_example.get("payload_format", "list"), normalized=True
    )
    prepared = payload_example_adapter(hass, payload_example, normalized, schema_data)
    if inspect.isawaitable(prepared):
        prepared = await prepared
    assert isinstance(prepared, PreparedPayload), (
        "Return the actual preparation result, not a validation claim"
    )
    assert isinstance(prepared.context, RenderContext), "Use the installed imagespec RenderContext"
    assert callable_origin(prepared.prepare).startswith(f"custom_components.{domain}"), (
        "Invoke the real integration rendering/preparation function"
    )
    assert not callable_origin(prepared.prepare).startswith("unittest.mock")
    assert prepared.payload == resolved_payload, (
        "Render the documented action payload after real HA/schema normalization"
    )
    issues = validate(prepared.payload)
    assert not issues, f"imagespec {version('imagespec')} validation failed: {issues}"
    assert set(prepared.render_options).issubset(
        {"width", "height", "rotate", "rotate_mode", "background", "dither"}
    ), "Use actual public render options"
    assert "width" in prepared.render_options and "height" in prepared.render_options
    if inspect.iscoroutinefunction(prepared.prepare):
        actual = await prepared.prepare()
    else:
        actual = await hass.async_add_executor_job(prepared.prepare)
        if inspect.isawaitable(actual):
            actual = await actual
    assert isinstance(actual, Image.Image), (
        "The real preparation path must produce an image without device I/O"
    )
    expected = await hass.async_add_executor_job(
        lambda: render(prepared.payload, context=prepared.context, **prepared.render_options)
    )
    assert actual.size == expected.size == tuple(payload_example["expected_size"]), (
        "Rendered dimensions differ from the documented device output"
    )
    assert actual.convert("RGB").tobytes() == expected.convert("RGB").tobytes(), (
        "Integration preparation and public renderer outputs differ"
    )
    allowed = {ImageColor.getrgb(color) for color in payload_example["expected_palette"]}
    colors = actual.convert("RGB").getcolors(maxcolors=actual.width * actual.height)
    assert colors is not None
    actual_colors = {color for count, color in colors}
    assert actual_colors.issubset(allowed), (
        f"Output contains colors outside the documented device palette: {actual_colors - allowed}"
    )
