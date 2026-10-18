# 개발·검사 안내

[English](development.md) | **한국어**

**이 리포 생성만으로 기존 리포의 파일이나 CI는 변경되지 않습니다.** 아래 검사는 읽기 전용입니다.

```bash
python3 -m pip install -r requirements_dev.txt
python3 scripts/audit_repositories.py --root .. --output /tmp/hass-ci-audit.json
python3 scripts/audit_repositories.py --github-owner eigger --output /tmp/hass-ci-remote.json
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

배지는 관리 구역 안에서만 갱신합니다. [사용법](documentation.md)을 먼저 확인하세요.

```bash
python3 scripts/sync_badges.py ../hass-example --check
```

중앙 템플릿 채택·검사 절차는 [사용법](../templates/integration/USAGE.md)을 따릅니다. 관리 영역 밖 README는 자동 수정하지 않습니다.

```bash
python3 scripts/check_integration.py ../hass-example
```
