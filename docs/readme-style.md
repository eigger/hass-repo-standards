# 통합 README 작성 형식

양언어 README의 사용자 본문을 정리할 때 사용하는 공통 기준입니다. `{...}`는 실제 리포에서 확인해 바꾸며 그대로 게시하지 않습니다. 기존 리포는 [README 규칙](documentation.md)과 변경 계획을 따릅니다. 이 문구는 작성자가 적용하며 중앙 렌더러가 기존 본문에 자동 삽입하지 않습니다.

## 제목과 소개

```markdown
# {표시 이름} for Home Assistant

A Home Assistant custom integration that {connects the device or service and describes the main function}.
```

```markdown
# {표시 이름} for Home Assistant

{기기 또는 서비스에 연결해 주요 기능을 제공하는} Home Assistant 커스텀 통합입니다.
```

이름·지원 대상·기능은 실제 구현을 따릅니다. 읽기 전용, 필수 서버 등 중요한 조건을 소개나 요구사항에 둡니다. 두 언어의 의미를 맞추고 제목에 이모지를 넣지 않습니다.

## 본문 순서와 제목

적용되는 절을 아래 순서로 배치하며 고유 절은 내용에 맞는 위치에 유지합니다. 해당하지 않는 절을 만들지 않습니다. 제목 변경 전에 기존 링크를 조사하고 필요한 참조를 갱신합니다. 영어 제목은 sentence case, 고유명사·기술 식별자는 실제 표기를 사용합니다.

| 영어 | 한국어 | 내용 |
|---|---|---|
| Supported devices / Features | 지원 기기 / 주요 기능 | 기기·기능과 확인된 지원 범위 |
| Requirements | 요구사항 | 지원 최소 버전과 필수 기기·서비스 |
| Installation | 설치 | 배포 경로, 다운로드, 재시작 조건, 수동 설치 |
| Configuration / Quick start | 설정 / 빠른 시작 | 등록, 인증, 최초 사용 |
| Important limitations | 중요 제한사항 | 제한, 안전·이전 안내 |
| Documentation | 문서 | 상세 안내·문제 해결·개발 문서 |
| Support / Related projects / License | 지원 / 관련 프로젝트 / 라이선스 | 중앙 관리 영역 |

기능에 따라 센서·액션·자동화·프록시·마이그레이션 등 고유 절을 추가할 수 있습니다. 코드 블록·표·기존 주의와 근거, 검증되지 않은 상태는 보존합니다. 강조는 안전·필수 조건 등 독자의 판단에 필요한 곳에 사용합니다. 기존 고유 배지와 본문 이모지는 의미를 확인해 처리하며, 모든 제목의 이모지는 제거합니다.

## 설치 문구

기존 `hass-standards:installation` 블록은 배지만 소유합니다. 아래 단계는 그 밖의 본문에 작성하며, 배지가 열리는 곳과 다운로드·설정 단계를 구분합니다. 기존 `hacs_repository` My 링크는 2026.11 이전에는 HACS, 이후에는 마켓플레이스를 엽니다. [카탈로그와 My 링크](https://contributors.home-assistant.io/marketplace/guides/catalog/).

**기본 카탈로그에 있는 통합:**

```markdown
1. On Home Assistant 2026.11 or later, open **Settings → Marketplace** and search for **{integration}**. On earlier supported versions, search the default HACS integration catalog. The button above opens the repository in the appropriate store.
2. Download **{integration}**. Restart Home Assistant if prompted.
3. Open **Settings → Devices & services → Add integration → {integration}**, or configure it when discovered.
```

```markdown
1. Home Assistant 2026.11 이상에서는 **설정 → 마켓플레이스**에서 **{통합}**을 검색합니다. 이전 지원 버전에서는 HACS 기본 통합 카탈로그에서 검색합니다. 위 버튼은 버전에 맞는 스토어의 저장소 화면을 엽니다.
2. **{통합}**을 다운로드합니다. 안내가 표시되면 Home Assistant를 재시작합니다.
3. **설정 → 기기 및 서비스 → 통합 추가 → {통합}**을 선택하거나 자동 발견된 항목을 설정합니다.
```

**사용자 지정 저장소인 통합:** 기본 목록 여부는 적용 시 공식 카탈로그에서 확인해 근거와 날짜를 기록합니다. 첫 단계는 다음 형식을 사용하고 나머지 다운로드·설정 단계는 위 형식을 따릅니다.

```markdown
1. On Home Assistant 2026.11 or later, open **Settings → Marketplace** and add `{repository URL}` as a custom integration repository. A GitHub connection is required for custom repositories. On earlier supported versions, add it to HACS **Custom repositories** with category **Integration**. The button above opens the repository in the appropriate store.
```

```markdown
1. Home Assistant 2026.11 이상에서는 **설정 → 마켓플레이스**를 열고 `{repository URL}`을 사용자 지정 통합 저장소로 추가합니다. 사용자 지정 저장소에는 GitHub 연결이 필요합니다. 이전 지원 버전에서는 HACS **사용자 지정 저장소**에 **통합** 유형으로 추가합니다. 위 버튼은 버전에 맞는 스토어의 저장소 화면을 엽니다.
```

지원 최소 버전이 2026.11 이상이면 이전 HACS 경로를 생략할 수 있습니다. 위 세 번째 단계는 실제 config flow가 있는 통합의 예시입니다. YAML 전용 통합은 통합 추가를 지시하지 않고 실제 YAML 설정과 재시작 안내로 연결합니다. 자동 발견이 없는 통합은 해당 문구를 넣지 않습니다. 기존 수동 설치는 실제 `custom_components/{domain}` 경로와 재시작을 안내합니다. 인증·기기 준비·제거·기존 버전 이관 안내와 예제는 삭제하지 않습니다. 마켓플레이스는 일부 통합을 즉시 불러오고 다른 경우 재시작 안내를 표시하므로 일률적으로 재시작을 필수로 단정하지 않습니다. [마켓플레이스 동작](https://contributors.home-assistant.io/marketplace/how-it-works/).

필요하면 설치 단계와 무관한 설정 절을 제외한 GitHub 전용 설치 안내를 `ha-marketplace:exclude-start`/`ha-marketplace:exclude-end`로 감쌀 수 있습니다. 중앙 관리 블록은 그대로 유지하고 기존 고유 안내가 마켓플레이스 화면에서 사라지지 않는지 확인합니다. [표시 제외 주석](https://contributors.home-assistant.io/marketplace/reference/repository-structure/).
