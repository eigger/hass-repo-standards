"""Minimal actual HA flow required to load the offline fixture config entry."""

from homeassistant import config_entries


class PayloadSampleConfigFlow(config_entries.ConfigFlow, domain="payload_sample"):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_abort(reason="not_supported")
