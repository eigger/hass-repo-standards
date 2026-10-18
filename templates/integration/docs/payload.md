# Payloads

[README](../README.md) | **English** | [한국어](payload.ko.md)

## Common payload guide

See the [imagespec payload guide](https://github.com/eigger/imagespec/blob/main/docs/payload.md) for the shared syntax, elements, properties, examples, colors, rotation and dithering.

## Using payloads in this integration

REPLACE_ACTION_DETAILS: name the actual supported action, target selection and nested payload location. Explain the integration’s real template preparation and where users call it. Preserve existing working instructions; do not invent an action merely to fill this template.

## Minimal working example

[Runnable action YAML](../examples/payload/minimal.yaml)

REPLACE_EXAMPLE_DETAILS: explain the linked complete action YAML, its actual model/target/context and expected result. Use the same registered file in both languages. This is a complete HA wrapper, not the library’s bare element list. Preserve its real list or YAML-string payload API; register payload_format according to the actual action YAML input and check how the real schema normalizes it.

## Device output settings

REPLACE_OUTPUT_DETAILS: actual model dimensions, resulting output size, supported palette, rotation mode/dither policy, font lookup and device/media limits. Distinguish host action fields from internal renderer options.

## Supported features and limitations

REPLACE_FEATURE_DETAILS: actual installed-version elements/extras, templates, font/image/history providers and device restrictions. Explain unavailable capabilities and N/A with reasons. No new feature or config entry is required just to populate a section.

## Troubleshooting

Use the integration's [existing Issues](https://github.com/REPLACE_REPOSITORY/issues).
