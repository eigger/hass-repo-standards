"""Offline HACS status validation and bilingual installation instructions."""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import urlencode, urlsplit


def status(config):
    value = config.get("hacs", "custom")
    if value not in {"custom", "default"}:
        raise ValueError("hacs must be custom or default")
    if value == "default":
        evidence = config.get("hacs_default_evidence")
        if not isinstance(evidence, dict) or set(evidence) != {"url", "checked_at"}:
            raise ValueError("Default needs hacs_default_evidence {url, checked_at}")
        url = evidence["url"]
        if not isinstance(url, str) or re.search(r"\s", url):
            raise ValueError("HACS Default evidence requires an HTTPS URL")
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("HACS Default evidence requires an HTTPS URL")
        checked = evidence["checked_at"]
        try:
            if not isinstance(checked, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", checked):
                raise ValueError
            date.fromisoformat(checked)
        except ValueError as error:
            raise ValueError("HACS Default checked_at must be a valid YYYY-MM-DD date") from error
    return value


def render(config, language, selected=None):
    selected = status(config) if selected is None else selected
    repository = config["repository"]
    if not isinstance(repository, str) or not re.fullmatch(
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository
    ):
        raise ValueError("repository must be owner/name")
    title = "## Installation" if language == "en" else "## 설치"
    prerequisite = (
        "[Install and configure HACS](https://www.hacs.xyz/docs/use/download/download/) first."
        if language == "en"
        else "먼저 [HACS를 설치하고 설정](https://www.hacs.xyz/docs/use/download/download/)하세요."
    )
    if selected == "default":
        owner, name = repository.split("/")
        url = "https://my.home-assistant.io/redirect/hacs_repository/?" + urlencode(
            {"owner": owner, "repository": name, "category": "integration"}
        )
        button = f"[![Open your Home Assistant instance and open a repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)]({url})"
        steps = (
            "1. Open the repository in HACS using the button above, or search for "
            f"`{repository}` in HACS.\n"
            "2. Download the integration in HACS, then restart Home Assistant."
            if language == "en"
            else "1. 위 버튼으로 HACS의 리포지토리를 열거나 HACS에서 "
            f"`{repository}`를 검색하세요.\n"
            "2. HACS에서 통합을 다운로드한 뒤 Home Assistant를 재시작하세요."
        )
        return f"{title}\n\n{prerequisite}\n\n{button}\n\n{steps}"
    base = f"https://github.com/{repository}"
    steps = (
        "1. Open HACS → ⋮ → Custom repositories.\n"
        f"2. Add `{base}` with type **Integration**.\n"
        "3. Find and download the integration in HACS, then restart Home Assistant."
        if language == "en"
        else "1. HACS → ⋮ → 사용자 지정 저장소를 여세요.\n"
        f"2. `{base}`를 **통합(Integration)** 유형으로 추가하세요.\n"
        "3. HACS에서 통합을 찾아 다운로드한 뒤 Home Assistant를 재시작하세요."
    )
    return f"{title}\n\n{prerequisite}\n\n{steps}"
