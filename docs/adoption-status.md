# 중앙 적용 현황

각 리포별 세션에서 수행한 공통 규칙 적용 결과를 모읍니다. 상세 판정·증거는 각 리포의 `ADOPTION_CHECKLIST.md`, 기준 커밋·예외는 `STANDARDS.md`에 기록하고 여기는 요약과 링크를 유지합니다. [채택 지침](adoption.md)과 [체크리스트 판정 기준](checklist.md)을 함께 따릅니다.

## 초기 등록 범위

**2026-10-17** GitHub 목록 기준으로 HA 통합 리포 25개(보관 리포 1개 포함)와 다른 유형 4개를 등록했습니다. 등록 이후 hass-kibble 파일럿을 시작했으며 결과는 아래 행에 기록합니다. 현재 적용 대상 HA 통합은 22개이며, 보관 리포 1개와 사용자 지정 2개는 제외합니다. 초기 `미착수`는 중앙에 작업 시작이 등록되지 않았다는 뜻이며, 해당 리포의 기존 기능·테스트 품질이 미흡하다고 판정한 것이 아닙니다. 전체 적용률을 자동 집계하지 않습니다.

## 상태 기준

| 상태 | 판정 |
|---|---|
| 미착수 | 적용 작업 시작 기록과 담당자가 아직 없음 |
| 진행 중 | 점검·구현·검증·리뷰·병합 진행 중. 중단·실패·원격 갱신 지연도 이유와 다음 조치를 남김 |
| 완료 | 적용 대상 필수 항목이 PASS 또는 근거 있는 N/A이고, 변경이 실제 기본 브랜치에 반영됐으며 해당 커밋의 검증 증거가 있음 |
| 예외 포함 | 기본 브랜치에 적용됐고 필수 TODO는 없지만 필수 EXCEPTION이 남음. 예외·담당자·재검토 조건을 연결 |
| 적용 제외 | archived·이전·다른 유형 등 제외 범위를 근거와 함께 명시 |

열린 PR이나 로컬 수정만 있으면 `진행 중`입니다. 필수 검사가 미실행·실패·대기 중이면 `완료`로 바꾸지 않습니다. 실제 기기 검증과 실제 HA 테스트는 구분합니다. 완료 판정은 행에 기록한 표준 SHA와 대상 커밋에 대한 것이며, 공통 규칙이 바뀌었다고 기존 결과를 새 기준의 검증 결과로 자동 재사용하지 않습니다.

## HA 통합 리포

| 리포 / 기본 브랜치 | 상태 | 적용 내용 | 근거: 기준 SHA·체크리스트·커밋/PR·CI | 남은 작업 / 제외 사유 | 갱신일 / 담당 |
|---|---|---|---|---|---|
| [hass-atflee](https://github.com/eigger/hass-atflee) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-ble-esl](https://github.com/eigger/hass-ble-esl) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-ble-led-sign](https://github.com/eigger/hass-ble-led-sign) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-catprinter](https://github.com/eigger/hass-catprinter) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-cyx-rgb-led](https://github.com/eigger/hass-cyx-rgb-led) / `master` | 적용 제외 | — | 2026-10-17 사용자 명시 | 사용자 요청으로 공통화 대상에서 제외. 별도 요청 전 수정하지 않음 | 2026-10-17 / 미배정 |
| [hass-divoom](https://github.com/eigger/hass-divoom) / `master` | 적용 제외 | — | 2026-10-17 사용자 명시 | 사용자 요청으로 공통화 대상에서 제외. 별도 요청 전 수정하지 않음 | 2026-10-17 / 미배정 |
| [hass-esphome-ota](https://github.com/eigger/hass-esphome-ota) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-garage](https://github.com/eigger/hass-garage) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-gicisky](https://github.com/eigger/hass-gicisky) / `master` | 적용 제외 | — | GitHub archived 상태 확인 | hass-ble-esl로 이전. 별도 요청 전 이관 대상에서 제외 | 2026-10-17 / 미배정 |
| [hass-icscale](https://github.com/eigger/hass-icscale) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-jaalee](https://github.com/eigger/hass-jaalee) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-kibble](https://github.com/eigger/hass-kibble) / `master` | 완료 | Core 대응 구조·실제 HA 테스트·공통 CI·문서/배지/지침·로컬 brand 적용. 지원 최소 HA 2025.3.0 / Python 3.13 / 플러그인 0.13.221 복원, current HA 2026.10.2 / Python 3.14 / 플러그인 0.13.373 유지. 최종 원격 독립 검증: 각 환경 31 passed, pip check·HACS 9개·Hassfest PASS | 기준 `103124f47c6fc838a39eddbd008e64cfb1a5e5f0` · [구현 커밋](https://github.com/eigger/hass-kibble/commit/f1a70396bea833b25e8fbcac7fa837ac3769ec91) · [마감 문서 커밋](https://github.com/eigger/hass-kibble/commit/d9f649c067880ce8b9bc42f826b16748d3b6a7b2) · [체크리스트](https://github.com/eigger/hass-kibble/blob/d9f649c067880ce8b9bc42f826b16748d3b6a7b2/ADOPTION_CHECKLIST.md) · [최종 Tests](https://github.com/eigger/hass-kibble/actions/runs/39034618553) · [최종 Validate](https://github.com/eigger/hass-kibble/actions/runs/39034618551) · 이전 채택 [PR #8](https://github.com/eigger/hass-kibble/pull/8) | 필수 TODO·현재 예외 없음. 구현 f1a·마감 문서 d9f649c의 최종 원격 CI와 체크리스트를 독립 확인함. 실서버·실기기·HA UI 표시 미검증은 별도 한계로 유지 | 2026-10-17 / 조율 root · 구현 implement_kibble_pilot · 공통 도구 implement_shared_pilot_support · 독립 리뷰 review_kibble_pilot |
| [hass-kma](https://github.com/eigger/hass-kma) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-kocom-smarthome](https://github.com/eigger/hass-kocom-smarthome) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-lywsd02](https://github.com/eigger/hass-lywsd02) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-magic-caster-wand](https://github.com/eigger/hass-magic-caster-wand) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-marklife](https://github.com/eigger/hass-marklife) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-melk-light](https://github.com/eigger/hass-melk-light) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-minibig](https://github.com/eigger/hass-minibig) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-niimbot](https://github.com/eigger/hass-niimbot) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-omron](https://github.com/eigger/hass-omron) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-opinet](https://github.com/eigger/hass-opinet) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-sip](https://github.com/eigger/hass-sip) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-vson](https://github.com/eigger/hass-vson) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-ws-bridge](https://github.com/eigger/hass-ws-bridge) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |

## 다른 유형의 리포

HA 통합 전용 구조·테스트를 강제하지 않습니다. 적용 범위를 먼저 정하고 해당 문서·CI 공통 항목만 점검합니다.

| 리포 / 기본 브랜치 | 적용 범위 | 상태 | 적용 내용 / 근거 | 남은 작업 | 갱신일 / 담당 |
|---|---|---|---|---|---|
| [hass-imagespec-card](https://github.com/eigger/hass-imagespec-card) / `main` | 카드: 문서·CI 공통 항목 | 미착수 | — / 미등록 | 적용 범위 점검 | 2026-10-17 / 미배정 |
| [hassble-android](https://github.com/eigger/hassble-android) / `main` | Android: 문서·CI 공통 항목 | 미착수 | — / 미등록 | 적용 범위 점검 | 2026-10-17 / 미배정 |
| [hassble-config](https://github.com/eigger/hassble-config) / `main` | YAML 설정: 문서·CI 공통 항목 | 미착수 | — / 미등록 | 적용 범위 점검 | 2026-10-17 / 미배정 |
| [hassio-apps](https://github.com/eigger/hassio-apps) / `master` | 앱: 문서·CI 공통 항목 | 미착수 | — / 미등록 | 적용 범위 점검 | 2026-10-17 / 미배정 |

## 로컬 checkout 참고

- `hass-coolled`: `hass-ble-led-sign`과 같은 원격을 사용하는 checkout이므로 별도 리포로 중복 집계하지 않습니다.
- `hass-timemore`: 로컬에는 있으나 이번 GitHub 목록에 없습니다. 원격 존재·접근 상태를 확인한 뒤 필요하면 통합 표에 등록합니다. 아직 적용 제외나 완료로 판정하지 않습니다.
- `hass-repo-standards`: 규칙과 공통 도구를 관리하는 이 리포 자체이며, HA 통합 적용 실적에 포함하지 않습니다.

## 갱신 절차

1. **작업 시작:** 최신 중앙 표를 읽고 해당 리포 행을 `진행 중`으로 바꿉니다. 주 에이전트/세션 식별자와 구현·독립 리뷰/검증 서브 에이전트, 검토한 표준 SHA, 작업 범위·다음 조치를 기록합니다. 새 리포는 실제 원격·기본 브랜치와 유형을 확인해 추가합니다.
2. **단계 변경:** 구조·실제 HA 테스트·의존성·CI·README/Bluetooth 등 적용한 항목, 남은 작업, 커밋/PR·CI 링크·리뷰/재검증 결과와 체크리스트 위치를 갱신합니다. 차단·중단이 생기면 이유와 재개 조건을 남깁니다.
3. **작업 종료·이관:** 기본 브랜치 반영과 체크리스트·실제 검증 결과를 확인해 위 상태 기준으로 기록합니다. 갱신일(Asia/Seoul)·담당자를 함께 적습니다. 완료 전 필수 TODO·예외를 누락하지 않습니다.
4. **병행 세션:** 최신 중앙 main과 비교해 자신의 리포 행만 수정하고 다른 담당자의 변경을 보존합니다. 다른 행을 덮어쓰거나 강제 푸시하지 않습니다. 충돌은 최신 내용에 자기 진행 기록을 합쳐 해결합니다.
5. **중앙 갱신이 불가능할 때:** 대상 리포의 체크리스트에 결과를 먼저 남기고, 최종 보고에 중앙 미반영 사유와 반영할 행 내용을 명시합니다. 중앙 표가 갱신됐다고 보고하지 않습니다.

근거 칸에는 기준 표준 전체 SHA와 검토 대상 커밋, 실제 존재하는 체크리스트·PR·CI 링크를 넣습니다. 아직 만들지 않은 파일·PR의 가짜 링크는 생성하지 않습니다. 직접 push한 작업은 commit 링크를 사용하고 PR을 임의로 만들지 않습니다. 정책·구현 변경이 생기면 각 문서의 원본을 수정하며, 현황표에 별도 규칙을 추가하지 않습니다.
