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

적용되는 절을 아래 순서로 배치하며 고유 절은 내용에 맞는 위치에 유지합니다. 해당하지 않는 절을 만들지 않습니다. 제목 변경 전에 기존 링크를 조사하고 필요한 참조를 갱신합니다. 영어 본문 제목은 sentence case, 고유명사·기술 식별자는 실제 표기를 사용합니다. 관리 영역의 관련 프로젝트 제목은 기존 릴리스와 호환되는 Related Projects를 유지합니다.

| 영어 | 한국어 | 내용 |
|---|---|---|
| Supported devices / Features | 지원 기기 / 주요 기능 | 기기·기능과 확인된 지원 범위 |
| Requirements | 요구사항 | 지원 최소 버전과 필수 기기·서비스 |
| Installation | 설치 | 마켓플레이스, 설치, 재시작 조건 |
| Configuration / Quick start | 설정 / 빠른 시작 | 등록, 인증, 최초 사용 |
| Important limitations | 중요 제한사항 | 제한, 안전·이전 안내 |
| Documentation | 문서 | 상세 안내·문제 해결·개발 문서 |
| Support / Related Projects / License | 지원 / 관련 프로젝트 / 라이선스 | 중앙 관리 영역 |

기능에 따라 센서·액션·자동화·프록시·마이그레이션 등 고유 절을 추가할 수 있습니다. 코드 블록·표·기존 주의와 근거, 검증되지 않은 상태는 보존합니다. 강조는 안전·필수 조건 등 독자의 판단에 필요한 곳에 사용합니다. 기존 고유 배지와 본문 이모지는 의미를 확인해 처리하며, 모든 제목의 이모지는 제거합니다.

## 요구사항 문구

영어·한국어에서 같은 항목 순서와 굵은 라벨을 사용합니다. 최소 HA 버전은 `hacs.json`의 버전을 그대로 씁니다. Bluetooth 조건과 지원 기기에는 실제 요구사항을 넣고, 통합에 해당하지 않는 항목은 생략합니다. 서버 등 필수 조건이 더 있으면 그 뒤에 추가합니다. 스토어 버전 구분은 설치 절에, 기기를 깨우는 등 설정 중 필요한 조치는 설정 절에 둡니다.

```markdown
- **Home Assistant:** {version} or later.
- **Bluetooth:** {required Bluetooth capability}.
- **Device:** {supported device}.
```

```markdown
- **Home Assistant:** {버전} 이상.
- **Bluetooth:** {필수 Bluetooth 연결 조건}.
- **기기:** {지원 기기}.
```

## 설치 문구

설치 제목 바로 아래에는 중앙 렌더러가 생성한 배지를 둡니다. 마켓플레이스에서 배지를 사용해 저장소를 열고, 필요하면 링크에서 직접 추가하는 절차를 안내합니다. 같은 설치 방식을 가진 리포는 본문에서 `{repository URL}`만 바꿉니다. [카탈로그와 My 링크](https://contributors.home-assistant.io/marketplace/guides/catalog/#the-link-to-your-repository).

```markdown
1. Click the badge above to open the repository in Marketplace.
2. If you need to add it yourself, go to **Settings → Marketplace → Add from link** and enter <{repository URL}>. Connect GitHub if prompted.
3. Select **Install**. Restart Home Assistant if prompted, then continue to [Configuration](#configuration).
```

```markdown
1. 위 배지를 클릭해 마켓플레이스에서 저장소를 엽니다.
2. 저장소를 직접 추가하려면 **설정 → 마켓플레이스 → 링크에서 추가**에서 <{repository URL}>을 입력합니다. 안내가 표시되면 GitHub 계정을 연결합니다.
3. **설치**를 선택합니다. 재시작 안내가 표시되면 Home Assistant를 재시작합니다. 설치가 끝나면 [설정](#설정)으로 이동합니다.
```

배지와 번호 목록 사이에 빈 줄을 둡니다. 설치 후 실제 등록·인증·YAML 설정은 연결된 설정 절에서 안내합니다. 기기별 준비, 제거, 마이그레이션 및 기존 예제는 내용에 맞는 절에 보존합니다. [마켓플레이스 동작](https://contributors.home-assistant.io/marketplace/how-it-works/).

필요하면 설치 단계와 무관한 설정 절을 제외한 GitHub 전용 설치 안내를 `ha-marketplace:exclude-start`/`ha-marketplace:exclude-end`로 감쌀 수 있습니다. 중앙 관리 블록은 그대로 유지하고 기존 고유 안내가 마켓플레이스 화면에서 사라지지 않는지 확인합니다. [표시 제외 주석](https://contributors.home-assistant.io/marketplace/reference/repository-structure/).
