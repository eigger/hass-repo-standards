# Changelog

## 2026-10-20 — Config subentry translation namespaces

- Resolve registered ConfigSubentryFlow types from literal ConfigFlow registration dictionaries, including local imported string constants and handler aliases, and check their `config_subentries.<type>.step`/`abort` keys instead of `config.step`/`abort`.
- Keep ordinary config/options checks and missing-key detection; unresolved subentry registrations fail explicitly rather than accepting duplicate fallback translations. Add multiple-type, abort, missing-key and unresolved-registration regressions.

## 2026-10-20 — Hassfest source compatibility prototype

- Add an optional reviewed full Core SHA path for the shared Hassfest job, preserving the default official action and failing on fetch/build/validation errors. This local prototype addresses published-image schema lag without altering caller manifests or support minima; actual image-build evidence remains separate.

## 2026-10-20 — manifest 제품 분류 검토

- HA-02에 실제 제품 categories 1–3개와 근거 기록, 제외 유형의 키 생략, 주 분류 순서·공식 slug·중복/부모-하위 분류 검사를 추가했습니다. upstream 선택 항목/HACS 누락 경고와 중앙 필수 정책을 구분합니다.
- sourced 입력·설정의 categories_review·오프라인 taxonomy snapshot·생성/조사/계획/정적 검사·체크리스트를 연결합니다. 기존 manifest는 자동 덮어쓰지 않으며 분류를 플랫폼에서 추정하거나 공통 기본값으로 채우지 않습니다. 중앙 변경만 수행하며 다른 통합·지원 최소·의존성·릴리스는 변경하지 않습니다.

## 2026-10-20 — HACS 집계 배지와 설치 링크

- 확인된 HACS Default 통합은 공식 HACS 데이터의 HACS Downloads, Custom은 manifest domain의 Analytics Usage를 표시하도록 공통 렌더러·규칙·체크리스트를 변경했습니다. 기존 고유 배지를 보존하고 상태 변경 시 이전 공통 집계 배지를 교체합니다.
- 양언어 README 템플릿·렌더러·검사에 실제 저장소의 My Home Assistant HACS 설치 배지를 추가했습니다. 기존 설치 본문·제목·예제를 보존하며 Custom 링크의 category=integration과 공식 owner/저장소 이름 매개변수를 사용합니다. 외부 통합 적용·지원 버전·의존성·릴리스는 변경하지 않습니다.

## 2026-10-19 — T6 중앙 생성·갱신 시나리오 검증

- 신규/기존 × 기본·imagespec·blesession·둘 다의 8조합과 누락 실패를 실제 중앙 CLI로 실행하는 9개 자동 회귀를 추가했습니다. 보존·멱등성·조건 제거 후 문서/예제 유지와 CI 확장 충돌을 검증했고 도구 186개와 별도 중앙 HA 6개, 총 192개를 실행해 성공했습니다. 실제 code head `07256a4932cdd80bbf3edae442c810700efc107a`의 PR #7 CI 네 검사가 통과했습니다. 병합 상태는 PR에서 별도로 확인합니다.
- 이번 중앙 도구·템플릿·스킬 요청은 T6 중앙 검증으로 마무리합니다. 외부 통합 도입·하드웨어·실제 최소/current HA 통합 성공은 범위 밖이며 중앙 채택 현황표도 변경하지 않습니다.

## 2026-10-19 — T5 신규 생성·기존 채택 스킬 작성

- 두 스킬의 짧은 진입 문서·조건별 workflow·최소 UI metadata를 추가하여 검토 SHA의 실제 중앙 CLI로 연결합니다. 중앙 규칙·템플릿·검사 코드를 스킬에 복제하지 않습니다.
- 신규/기존/검토만 요청을 분기하고 기존 승인 범위의 적용은 중복 승인 없이 진행합니다. 입력 부재·충돌·CLI 실패와 실제 HA/번역/기기 미검증을 그대로 기록합니다.
- 명시적 설치·갱신 방법은 사용 안내에 기록하며 설치본의 상대 경로로 중앙 checkout을 추정하지 않습니다. 이번 작업은 중앙 원본 작성이며 실제 설치·외부 통합 적용은 수행하지 않았습니다. 정적 문법 검사와 독립 행동 검증은 별도 기록합니다.
- 격리 행동 평가에서 실제 requirement가 같은 기존 파일도 주석 차이로 충돌하는 문제와 생성 Dependabot의 실제 최소 파일 제외 누락을 발견했습니다. 유효 requirement 줄이 같을 때만 기존 바이트를 보존하고 실제 minimum/current 경로로 제외를 구성하도록 좁게 수정했습니다. 최종 도구 177개와 별도 중앙 HA 6개를 실행해 성공했으며 원행동·중간 재평가·최종 도구 결과를 구분합니다. 실제 bot·설치·자동 발동·실제 통합 완성 검증으로 해석하지 않습니다.

## 2026-10-19 — T4 생성물 검사·중앙 계약 연결 구현

- 중앙 저장소 검사에 계약·스키마·작성 자산 렌더링·원본 등록·이미 구현한 단계 리소스 검사를 연결합니다. 중앙 자산의 의도적인 TODO와 실제 적용된 통합의 미완성을 구분합니다.
- 생성물의 선택 기능·활성 대응 테스트·번역 키/placeholder·SHA·정확한 작성 기반 미완성 표시 검사를 기존 check 진입에 연결했습니다. 독립 코드 검증은 도구 166개와 별도 중앙 HA 6개를 실행해 성공했으며 실제 HA 동작·번역 의미 검증과 구분합니다. workflow/action 파일 자체는 변경하지 않고 caller checkout·action_path·CLI 호환과 기존 승인 예외 경로를 유지합니다.

## 2026-10-19 — T3 작성 기반과 보호된 적용·복구 구현

- 중앙 컴포넌트·테스트·번역 작성 자산 18개를 추가하고 manifest·hacs·선택 기능을 확인한 입력에서 렌더링합니다. 미작성 기기 동작·fixture·검증은 TODO·예외·pending으로 남깁니다.
- 내장 입력·동일 SHA 재계획·guards·원래 루트 존재 상태를 검증하는 apply와 대상 밖 journal 원본·현재 해시를 사용하는 recover를 추가합니다. 이전 T2 계획은 새 SHA에서 재생성하며 신규 create 후 adopt 재계획으로 추가 변경 없음을 확인합니다.
- T3 독립 코드 검증은 도구 140개와 중앙 HA 6개를 각각 실행해 성공했습니다. 생성 초안의 실제 HA negative smoke는 loader 이후 의도한 미구현 예외에 도달함을 확인했으며 실제 최소/current HA 통합 성공은 아닙니다. 커밋/CI 확인, 기기·외부 리포 적용과 후속 전체 계약 검사·스킬은 남아 있습니다.

## 2026-10-19 — T2 읽기 전용 조사·변경 계획 구현

- `manage_integration.py inspect/plan`과 실제 메타데이터·출처·선언 충돌·미확인 상태 조사를 추가합니다. 대상 파일을 변경하지 않고 대상 밖에 조사 결과·계획을 기록합니다.
- 같은 입력·SHA·대상 상태에서 같은 diff·guards를 만들며 계획에 검증한 입력 스냅샷과 canonical JSON digest를 포함합니다. 깨끗한 기준 checkout·원격 자격 정보 제거·동시 변경·출력 경계를 검증합니다.
- 현재 실행 명령과 fixture 입력은 [사용 안내](docs/template-skill-usage.md)에, 단계별 결과는 [검증 기록](docs/template-skill-validation.md)에 기록합니다. apply·새 컴포넌트 작성 기반·전체 계약 검사 연결·스킬과 외부 통합 적용은 미완료입니다.

## 2026-10-19 — T1 적용 계약과 공통 렌더러 구현

- 적용 계약 44개 레코드와 입력·조사·계획 JSON 스키마 및 외부 의존성을 추가하지 않는 스키마 검증기를 추가합니다. 기존 원본 21개와 후속 작성 자산 23개를 available/pending으로 구분합니다.
- README·배지 렌더링과 라이브러리 사용 조건을 공통 모듈로 옮기고 기존 도구의 공개 진입점을 유지합니다. 허용 경로 토큰은 검증한 domain과 선택 플랫폼으로 제한합니다.
- 단계별 구현·독립 검증 근거는 [검증 기록](docs/template-skill-validation.md)에 남깁니다. inspect/plan/apply CLI·신규 작성 기반·두 스킬과 실제 통합 도입은 후속 단계이며 이번 변경으로 외부 통합을 수정하지 않습니다.

## 2026-10-19 — 템플릿·스킬 작업지시서와 에이전트 지침 정리

- 구조 개편 설계에 단계별 파일·입출력·구현 동작·테스트·완료 조건을 명시한 T1~T6 작업지시서를 연결합니다. 공통 형식을 수동으로 다시 작성하는 대신 중앙 계약·템플릿·동일 렌더러를 사용하는 생성·갱신·검사 경로를 구현하도록 지정합니다. 도구·스킬 구현과 실제 통합 도입은 아직 미착수입니다.
- AGENTS.md의 반복된 README·Bluetooth·payload·테스트·의존성 세부 설명을 제거하고 필수 실행 원칙·작업지시서·채택 순서·작업별 계약 진입점으로 정리합니다. 규칙 ID·필수/권장 수준·지원 최소·본문 보존·독립 검증·중앙 현황·비설치 정책은 유지합니다.
- 기존 채택 리포의 파일·고정 SHA·CI를 자동 변경하지 않습니다. 새 기준은 각 리포의 다음 채택·재검토 범위에서 검증하며 과거 PASS를 재사용하지 않습니다.

## 2026-10-18 — imagespec 공통 payload 원본과 실제 예제 검증

- 공통 사용자 문법·속성·요소·색상·회전·디더링 원본을 imagespec의 양언어 payload 문서로 연결합니다. 중앙 DOC-08은 기기별 양언어 여섯 절과 실제 액션/대상/전체 YAML·출력/제약·기존 지원 경로를 강제하며 기존 README·기기 예제를 보존합니다. 제보 양식을 새로 만들지 않습니다.
- 모든 연결된 로컬 액션 YAML을 payload.examples에 실제 중첩 경로·기대 출력 크기·모델 색상으로 등록합니다. Validate 정적 검사에 더해 중앙 pytest 계약으로 실제 HA fixture·등록 스키마·통합 준비 경로·설치된 imagespec.validate/render 결과를 검증합니다. skip/xfail/deselect·자체 PASS 선언은 실행 증거가 아닙니다.
- 실제 액션 payload가 목록 또는 YAML 문자열인 기존 API를 보존하고 payload_format으로 스키마 정규화 결과를 구분합니다. marker 비활성 matrix는 명시적 N/A·버전 검증 없음으로 일반 HA 회귀를 유지하며 다른 활성 환경의 current/정확한 하한 검증은 필수입니다. 활성 환경 누락은 실패하고 설치·최소 상향으로 우회하지 않습니다.
- 공용 Tests/updater는 reusable workflow와 같은 검토 full standards-ref를 별도로 checkout하며 caller·기존 resolver 설치 버전을 유지합니다. current/정확한 하한은 실제 환경에서 검증하고 exact pin의 같은 설치값만 결과를 재사용합니다. 최소 HA·Python·라이브러리·릴리스 정책을 임의 변경하지 않습니다.
- 사용하지 않는 액션·기능·config entry를 검사 때문에 만들지 않습니다. 내부 렌더링 전용·YAML 설정 등 범위 차이는 실제 근거·중앙 계약 개선 또는 명시적 승인 예외로 다루며 정적 예외가 런타임 검사를 자동 면제한다고 주장하지 않습니다. 실물·기기 전송·원격 CI는 실제 수행 근거와 구분합니다.
- imagespec 공통 원본을 실제 기본 브랜치에 먼저 반영·URL 검증한 뒤 중앙 규칙을 공개합니다. 로컬 초안만으로 원격 공개나 기존 통합 적용을 완료했다고 보고하지 않습니다. 현재 사용자 브랜치·기존 작업을 보존하며 자동 commit/push·다른 통합 수정·릴리스를 수행하지 않습니다.

## 2026-10-18 — blesession 공통 안내 이관과 기기별 문제 해결 강제

- 공통 프록시 추천·설정·HA 등록·일반 문제 해결 원본을 blesession의 양언어 bluetooth/troubleshooting 문서로 옮깁니다. 기존 중앙 bluetooth URL과 troubleshooting 앵커는 짧은 이전 안내로 유지하며 중복 원본을 관리하지 않습니다. 일반 안내 읽기에 라이브러리 설치를 요구하지 않습니다.
- 중앙은 DOC-07 작성 규칙과 양언어 기기별 문제 해결 템플릿을 관리합니다. blesession 사용 통합은 고정 제목·순서·증상 표·실제 진단/로그·기존 Issues 연결을 적용하며 기존 README·기기 안내를 보존하고 제보 양식을 새로 만들지 않습니다.
- 공용 Validate의 검사기에 requirement 정규 이름(extras·연산자·marker 포함)·실제 import 식별과 언어별 문서/링크/placeholder 검사를 추가합니다. 실제 기기·진단 의미·번역·원격 지원 상태는 독립 리뷰가 필요합니다. 프록시만 지원하는 통합의 기존 문서 범위는 수동 검토하며 기존 채택 리포·과거 현황은 변경하지 않습니다.
- 독립 standards 검사 job은 현재 통합·테스트의 Python 3.14 문법을 파싱하도록 Python 3.14를 사용합니다. 로컬 검사기도 대상 문법 이상 버전으로 실행하며 구문 오류는 실제 파일·검사 Python을 표시합니다. 이는 도구 환경 선택으로 지원 최소 HA/Python을 변경하지 않으며 중앙 도구 단위 테스트의 Python 3.9 호환성을 유지합니다.

## 2026-10-18 — 중앙 템플릿 강제와 README 보존 경계

- README 공통 영역만 중앙 템플릿으로 강제하고 header/support/related-projects/license 관리 주석으로 수정 경계를 지정합니다. 그 밖의 세부 구성·순서·제목·본문은 리포에 맡기며 공통 적용 때문에 전면 재작성하거나 상세 내용을 이동하지 않습니다. 이 기준이 이전의 README 전체 순서·상세 내용 분리 지침을 대체합니다.
- 상단은 프로젝트명·한 줄 소개·언어 링크·flat 배지, 배지는 Release/HACS/HA minimum/Tests/Validate/License/Usage 순서입니다. 기존 고유 배지는 뒤에 보존합니다. 하단은 지원·확인된 관련 프로젝트·실제 라이선스와 기존 고지입니다. 양언어는 같은 구조·내용으로 번역하고 의미·누락을 독립 리뷰합니다.
- 실제 양언어 README와 테스트 기본 템플릿, 자동 준수 검사를 추가합니다. 세 빈 init와 루트 conftest를 고정하며 domain fixture·실제 HA 로딩·기존 회귀 범위를 유지하고 공통 오류 무시·네트워크 일괄 허용·로딩 우회를 금지합니다.
- 공용 CI 명칭·파일명·기존 실행 조건을 강제하며 전용 CI는 공통 명명 형식을 따릅니다. 차이는 중앙 템플릿 수정·검증 또는 사용자의 명시적 승인 후 적용하고 근거·범위를 기록합니다. 승인은 에이전트와 사용자 사이의 절차이며 CI 승인 대기 기능을 추가하지 않습니다.
- 기존 채택 리포를 자동 수정하거나 표준 SHA·CI 고정을 일괄 갱신하지 않습니다. 각 리포의 다음 적용·재검토 때 영향과 검증을 기록합니다. 과거 CHANGELOG·중앙 현황은 역사적 기록으로 보존합니다.

## 2026-10-18 — Bluetooth 사용자 안내와 작성 규칙 분리

- 기본 영어 Bluetooth 사용자 안내와 한국어 대응판을 제공하고 기기 선택 → 펌웨어 설치 → HA 등록 → 연결 확인 → 문제 해결 순서로 재작성합니다. XIAO W5500 V1.2와 USB-A 동글형 AtomS3U 추천·구매 링크를 유지하며 실제 공식 설치 지원·직접 빌드 경로를 구분합니다.
- 작성자 지시·통합별 문서 요구·blesession 구현 계약은 별도 bluetooth-documentation.md로 옮깁니다. DOC-07과 AGENTS·README·채택 안내·체크리스트·템플릿은 사용자에게 해당 언어의 사용자 문서를 연결하고 개발 가이드를 설정 안내로 노출하지 않도록 맞춥니다. 기존 규칙 ID·필수 수준 및 중앙 AGENTS 비복사 정책을 유지합니다.
- 공식 HA·ESPHome·Seeed·M5 자료로 절차를 재확인합니다. 설정 예제와 문서 검증은 실물·펌웨어 컴파일 검증과 구분합니다.

## 2026-10-18 — 공통 적용 지침의 중앙 실행과 로컬 설치 중단

- 중앙 AGENTS.md는 공통 규칙 적용 작업 때 직접 읽는 실행 지침으로 유지합니다. 통합 리포의 AGENTS.md로 복사·생성·추가하거나 다른 파일명으로 에이전트 진입 지침을 설치하지 않으며, 사용자 별도 요청 없이 재설치하지 않습니다. 복사용 AGENTS.md 템플릿과 설치 안내를 제거합니다.
- 이후 채택·재검토는 중앙 경로나 URL을 지정해 진행하고, 통합에는 STANDARDS.md의 검토 SHA·예외와 ADOPTION_CHECKLIST.md의 해당 시점 검증 근거를 남깁니다. 과거 PASS는 이후 변경의 검증 결과로 사용하지 않습니다. 기존 리포 고유 지침은 임의로 수정·삭제하지 않습니다.
- 구현과 독립 리뷰·검증의 서브 에이전트 위임 및 중앙 현황 갱신 절차는 유지합니다. 기존 채택 리포의 공통 진입 지침 설치를 이후 작업의 전제로 삼지 않습니다. 이 변경만으로 다른 리포를 자동 수정하거나 기록된 표준 SHA·CI 고정을 일괄 갱신하지 않습니다.
- 과거 CHANGELOG와 중앙 현황표의 AGENTS 적용·검증 언급은 당시 수행한 작업의 역사적 기록으로 보존하며, 현재 설치 지시로 해석하지 않습니다.

## 2026-10-17 — 간결한 README와 BLE 문제 해결 안내

- BLE ESL의 문서 연결 방식을 참고해 메인은 핵심 소개·요구조건·빠른 시작·짧은 예제·문서 목록·지원/라이선스로 유지하고 상세 옵션·긴 YAML·참조·개발 명령은 추가 문서로 보존·분리하도록 명확히 합니다. 중요 제한·안전·미검증 고지는 메인에도 남깁니다.
- blesession 통합은 전용 문제 해결 문서 또는 공통 문서 링크와 모델 고유 조건·진단 경로를 제공합니다. 공통 Bluetooth 안내에 오류 단계·스캔/GATT 구분·연결 끊김·제보 정보를 보완하며 BLE ESL 전용 옵션을 일반화하지 않습니다.
- 중앙 README의 긴 개발·검사 명령은 양언어 상세 개발 문서로 이동합니다.

## 2026-10-17 — Usage 배지와 README 언어 정책 수정

- README 필수 구성에 개발·참여, 실제 활성 Issues/Discussions 지원 경로와 LICENSE 파일 링크를 명확히 합니다. 비활성 기능은 임의로 활성화하지 않고 사용 가능한 대체 지원 경로를 안내합니다.

- 모든 HA 통합의 manifest domain으로 동적 Usage 배지를 미리 생성합니다. 사전 조회·Analytics 근거·analytics 활성화 조건을 제거하며 조회 실패/미집계를 설치 수 0으로 해석하지 않습니다.
- 기본 README.md는 영어, README.ko.md는 한국어로 제공하고 상호 연결합니다. 기존 내용은 보존하며 중앙 README·지침·체크리스트·템플릿을 함께 맞춥니다. 상세 개발 규칙은 한국어를 유지할 수 있습니다.
- hass-kibble의 후속 README/Usage 보완을 중앙 현황표에 진행 중으로 등록합니다.

## 2026-10-17 — hass-kibble 파일럿 지원

- 파일럿에서 테스트 최신화와 지원 최소를 혼동한 사례를 바로잡아 공통·로컬 AGENTS, 체크리스트와 STANDARDS 메타데이터에 세 축 분리·착수 전 선언 확인·독립 리뷰 및 봇 PR 검사를 명시합니다. 다음 통합은 최신화 요청으로 지원 범위를 바꾸지 않고 실제 비호환 근거와 별도 명시적 승인 여부를 확인합니다.
- hass-kibble PR #8 squash merge 이후 사용자가 최신 테스트와 지원 최소를 별개로 재확인했습니다. f1a7039 커밋에 기존 최소 HA 2025.3.0과 독립 검증 환경을 복원하고 현재 HA 2026.10.2 테스트를 유지했습니다. 마감 문서 d9f649c에서 두 환경 각각 31개 테스트·pip check·HACS 9개·Hassfest의 원격 성공과 필수 TODO·현재 예외 없음을 독립 확인하여 적용을 완료했습니다. 실서버·실기기·HA UI 표시는 미검증 한계로 구분합니다.
- 최신 테스트 실패는 호환 문제를 수정·재검증하고, 새 API 등 실제 비호환 근거와 별도 명시적 승인 없이 테스트 최신화를 이유로 지원 최소를 올리거나 최소 환경을 제거하지 않도록 명확히 합니다.
- Dependabot 예시에 과거 최소 환경 제외·HA/플러그인 묶음을 추가하고 실제 기본 브랜치 비교·다운그레이드 거부·Python/정확한 HA 검사값/지원 메타데이터 동기화를 명확히 합니다.
- 파일럿의 실제 HACS 실패를 반영해 HACS-05의 로컬 브랜드 자산·원격 등록 fallback과 이미지 확인 절차를 명확히 합니다. 기존 규칙 ID와 필수·권장 수준은 유지합니다.
- hass-kibble 첫 적용을 등록하고 hass-cyx-rgb-led·hass-divoom은 사용자 요청으로 제외합니다. 적용 대상 HA 통합은 22개입니다.
- 공통 HA 환경에서 실제 테스트 플러그인 설치·버전을 확인하고, 생략한 pytest 경로는 domain 구조로 결정합니다. 기존 unit caller는 유지합니다.
- 실행용 템플릿에 정확한 최소/현재 HA별 Python·requirements·버전 검사와 실제 HA 테스트 경로를 반영합니다. 예시 버전은 각 통합의 실제 지원 범위에 맞춰 변경해야 합니다.


## 2026-10-17 — Bluetooth 추천 기기 정리

- Olimex 추천을 제거하고 XIAO W5500 V1.2를 기본 추천으로, USB-A 동글 형태의 M5Stack AtomS3U를 추가하고 구매 링크를 병기.
- AtomS3U는 ESPHome 공식 목록 대상이 아님을 밝히고, 기존 설정의 `ble.disable`·`esp32_improv`를 삭제하고 합치도록 안내.
- M5Stack 제품 문서를 docs/sources.md에 추가.

## 2026-10-17 — 중앙 적용 현황과 에이전트 진입 지침

- GitHub 목록 기준 통합 25개와 다른 유형 4개의 중앙 적용 현황표 추가. 실제 적용 실적은 미착수로 시작하고 archive·중복·원격 확인 대상을 구분.
- 작업 시작·단계 변경·종료 때 중앙 표의 자기 리포 행을 갱신하도록 GOV-04 및 로컬/중앙 AGENTS 지침 정의.
- 공통 지침을 읽고 별도 세부 지시 없이 점검·적용·검증·보고하는 시작 절차 추가.
- 구현과 독립 리뷰·검증을 별도 서브 에이전트에게 위임하도록 GOV-05에 명시.
- 체크리스트·STANDARDS·README를 중앙 현황과 연결. 기존 통합의 코드·CI·AGENTS는 변경하지 않음.

## 2026-10-17 — 통합별 적용 체크리스트

- 기존 공통 규칙 ID에 대응하는 적용 체크리스트 사용법과 복사용 템플릿 추가.
- 미확인·적용·예외·해당 없음의 구분, 파일·CI·버전 조합 증거와 예외 재검토 기준 정의.
- README, 채택 안내, STANDARDS 및 에이전트 안내에서 점검표로 연결.
- 개별 통합의 적용 상태는 자동 판정하거나 완료 처리하지 않음.

## 2026-10-17 — Core 대응 구조와 실제 HA 테스트 규칙

- HACS 배포 차이를 제외하고 Core와 유사한 구현·테스트 구조로 작성하도록 명시.
- tests/components/<domain>/ 배치와 실제 HA fixture·config entry·플랫폼 로딩 검증을 필수로 정의.
- HA 코어 stub 금지, 외부 통신 경계 mock 허용 범위와 최소 버전 검증 기준 구체화.
- 패키지·HA 구성요소·테스트 도구의 의존성 선언 위치와 추가 절차 정의.
- Bluetooth proxy 설정·추천 기기 공통 문서 작성 및 해당 통합 README의 직접 안내/링크 규칙 추가.
- 이번 변경은 공통 규칙 문서에 한정. 실행용 템플릿·CI 구현·개별 통합 전환은 이후 작업.

## 2026-10-17 — 관리 방식 정리

- 규칙 리포는 태그·GitHub Release 없이 main과 커밋 이력으로 관리.
- 문서·템플릿은 main을 참조하고, 실제 채택 시 검토한 커밋 SHA로 고정하도록 정리.
- 기존에 생성한 두 태그 정리. 개별 HA 통합의 릴리스 규칙은 유지.

## 2026-10-17 — 리뷰 수정

- 현재 환경에서 marker가 비활성인 선택 의존성은 검증 없이 갱신하지 않고 실패하도록 수정.
- 성공적으로 변경 없음이 확인될 때도 기존 dependency PR과 branch를 동기화·정리하도록 수정.
- Python/운영체제 marker 및 yanked 제안의 회귀 테스트 추가.
- 수정된 updater action의 commit SHA로 중앙 workflow 참조 갱신.

## 2026-10-17 — 초기 작성

- HA·HACS·문서·배지·테스트·CI·의존성·릴리스 규칙 초안 확정.
- hass* 전체 로컬 CI 조사와 profile별 이관 계획 작성.
- HACS/Hassfest, Python test matrix, imagespec/blesession 등 manifest updater 재사용 workflow 제공.
- 최소 패키지 검사, 환경 설치 composite action, 배지 도구와 호출 템플릿 제공.
- 기존 통합 리포의 수정·workflow 호출·bot PR 생성은 포함하지 않음.
