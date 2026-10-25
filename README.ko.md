# Home Assistant Repository Standards

[English](README.md) | **한국어**

eigger의 Home Assistant 커스텀 통합을 위한 공통 규칙·템플릿·재사용 workflow입니다. 표준은 immutable exact `vX.Y.Z` 릴리스와 해석한 전체 커밋 SHA를 함께 기록하며, moving tag·branch·`latest`는 표준 참조로 사용하지 않습니다.

## 전체 리포 합계

**25개 리포** · **릴리스 asset 다운로드 2,346회** · **스타 452개** · **포크 79개**

2026-10-25 (Asia/Seoul) GitHub API 스냅샷입니다. 리포별 동적 수치·집계 기준·범위는 [리포별 배포·관심 현황](docs/repository-stats.ko.md)에 있습니다.

## 문서

[문서 구조](docs/index.md)에 규칙·템플릿·도구·참조를 역할별로 정리했습니다. 현재 이관 상태는 [중앙 적용 현황](docs/adoption-status.md)에서 확인합니다.

## 적용 방법

에이전트에게 **“hass-repo-standards 공통 규칙 적용해줘”**라고 요청하세요. 적용 작업은 [AGENTS.md](AGENTS.md), 적용되는 규칙과 [통합 템플릿 사용 안내](templates/integration/USAGE.md)를 읽고, `STANDARDS.md`에 검토한 릴리즈/SHA·승인 예외를, `ADOPTION_CHECKLIST.md`에 검증 근거를 기록합니다.

## 지원

- [Issues](https://github.com/eigger/hass-repo-standards/issues): 버그 신고와 기능 요청

## 라이선스

[MIT License](LICENSE)로 배포됩니다.
