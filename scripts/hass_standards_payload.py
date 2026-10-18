"""Runtime-owned pytest collection of documented payload examples in caller domain scope."""

from __future__ import annotations

import functools
import importlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from payload_documents import SCAFFOLD, examples


@dataclass
class PreparedPayload:
    """Real integration preparation result; never a claimed validation flag."""

    payload: list
    context: Any
    render_options: dict
    prepare: Any


def safe_path(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes caller repository: {relative}")
    return path


def callable_origin(callback):
    while isinstance(callback, functools.partial):
        callback = callback.func
    return getattr(callback, "__module__", type(callback).__module__)


def pytest_configure(config):
    root = Path(os.environ["PAYLOAD_REPOSITORY"]).resolve()
    domain = os.environ["PAYLOAD_DOMAIN"]
    settings = json.loads(safe_path(root, ".hass-standards.json").read_text())
    config._standards_payload_root = root
    config._standards_payload_domain = domain
    config._standards_payload_examples = examples(root, settings, safe_path)
    config._standards_payload_reports = {}
    config._standards_payload_path = safe_path(
        root, Path("tests/components") / domain / "test_payload_examples.py"
    )
    if config._standards_payload_path.read_text() != SCAFFOLD:
        raise pytest.UsageError("Missing or modified central payload contract scaffold")


class PayloadModule(pytest.Module):
    def _getobj(self):
        return importlib.import_module("hass_standards_payload_tests")


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makemodule(module_path, parent):
    if module_path.resolve() == parent.config._standards_payload_path.resolve():
        return PayloadModule.from_parent(parent, path=module_path)


def pytest_generate_tests(metafunc):
    if metafunc.function.__module__ == "hass_standards_payload_tests":
        entries = metafunc.config._standards_payload_examples
        metafunc.parametrize("payload_example", entries, ids=[entry["path"] for entry in entries])


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if item.module.__name__ == "hass_standards_payload_tests":
        item.config._standards_payload_reports.setdefault(item.nodeid, {})[report.when] = (
            report.outcome
        )


def pytest_sessionfinish(session, exitstatus):
    reports = session.config._standards_payload_reports
    expected = len(session.config._standards_payload_examples)
    completed = sum(
        values.get("setup") == values.get("call") == values.get("teardown") == "passed"
        for values in reports.values()
    )
    if completed != expected:
        session.exitstatus = 1
        terminal = session.config.pluginmanager.getplugin("terminalreporter")
        if terminal:
            terminal.write_line(
                f"Payload contract required {expected} executed examples, got {completed}; skips/xfail/deselection do not pass",
                red=True,
            )
