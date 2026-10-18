"""Actual HA fixture activation for runtime checker regressions."""

import pytest


@pytest.fixture(autouse=True)
def enable_integrations(enable_custom_integrations):
    pass
