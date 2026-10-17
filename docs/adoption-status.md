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
| [hass-atflee](https://github.com/eigger/hass-atflee) / `master` | 완료 | Core 대응 구조·실제 HA 테스트·공통 CI·blesession 하한·영문/한글 README·동적 Usage·사용/문제 해결 docs·진입 지침 적용. 지원최소 HA2025.8.0·통합0.6.1·blesession>=0.9.0 유지. 부분setup/GATT취소·서비스맵변경·개인로그 보호 보완 | 기준 `ff46b0c8d9ba53b1d35ab9a4aa38f4db26c06870` · [구현 master 커밋](https://github.com/eigger/hass-atflee/commit/4da5699c75021e272442165473ba6655f9f90e5c) · [체크리스트](https://github.com/eigger/hass-atflee/blob/ca595ad0a6b5d081e288c34121cf22912b89f809/ADOPTION_CHECKLIST.md) · [구현 Tests](https://github.com/eigger/hass-atflee/actions/runs/39039498134) · [구현 Validate](https://github.com/eigger/hass-atflee/actions/runs/39039498020) · [중앙 종료보고](https://github.com/eigger/hass-repo-standards/commit/9941581fe3c4428ddef669a5db028c9dbef3a87a) · [마감 문서 커밋](https://github.com/eigger/hass-atflee/commit/ca595ad0a6b5d081e288c34121cf22912b89f809) · [최종 Tests](https://github.com/eigger/hass-atflee/actions/runs/39039798232) · [최종 Validate](https://github.com/eigger/hass-atflee/actions/runs/39039798231) | 구현4da5699·마감문서ca595ad master 반영 및 정확한 각SHA 원격 Tests4matrix 각179passed skip0·pipcheck·lint2, HACS9checks(brands포함)·Hassfest 독립 성공 확인. 원격 current Python3.14.8/HA2026.10.2/플러그인0.13.373/pycares5.2, 최소Python3.13.16/HA2025.8.0/플러그인0.13.269/pycares4.11; blesession0.9.0(양mode). 로컬구현4환경/독립2환경 각179passed, 기존109함수156case 유지+신규23. 중앙구현·검증 종료9941581 및 최종 체크리스트 반영 완료; 필수 PASS/N/A·현재 TODO/예외 없음. 실물·새proxy보드·HA UI 미검증 | 2026-10-17 / 조율 root · 구현 atflee_implementation / atflee_docs · 독립 리뷰 review_atflee |
| [hass-ble-esl](https://github.com/eigger/hass-ble-esl) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-ble-led-sign](https://github.com/eigger/hass-ble-led-sign) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-catprinter](https://github.com/eigger/hass-catprinter) / `main` | 완료 | 실제 HA 테스트·공통 CI·imagespec/blesession 하한 검증·영문/한글 README·동적 Usage·기기별 Bluetooth 문제 해결·진입 지침 적용. 지원 최소 HA 2025.2.0 유지, current HA 2026.10.2. 부분 setup 실패/취소·GATT 링크 복구 지적 수정 | 기준 `78d242092eac732a1af48770e77e3f51e566c6c2` · [구현 main 커밋](https://github.com/eigger/hass-catprinter/commit/36419ac76e7e148a84efa7acdd6a1c964c85dfa5) · [체크리스트](https://github.com/eigger/hass-catprinter/blob/8093cbb63ab0e5c8326e271bbfc722f2d3c470a1/ADOPTION_CHECKLIST.md) · [구현 Tests](https://github.com/eigger/hass-catprinter/actions/runs/39036837387) · [구현 Validate](https://github.com/eigger/hass-catprinter/actions/runs/39036837361) · [마감 문서 커밋](https://github.com/eigger/hass-catprinter/commit/8093cbb63ab0e5c8326e271bbfc722f2d3c470a1) · [최종 Tests](https://github.com/eigger/hass-catprinter/actions/runs/39037166381) · [최종 Validate](https://github.com/eigger/hass-catprinter/actions/runs/39037166247) | 구현36419ac·마감문서8093cbb main 반영 및 중앙 구현·검증 종료보고 등록 완료. 독립 로컬 current Python3.14.5/HA2026.10.2/플러그인0.13.373 및 최소 Python3.13.14/HA2025.2.0/플러그인0.13.210 각84passed6skipped·pipcheck PASS. 6skip은 선택 dark PNG4개 미제공·base이미지 hDPI검사2개 해당없음이며 실제HA검사 skip 없음. 구현4mode는 초기80개 tree의 설치검증 이력, 최종84개는 동일 설치값의 양HA 및 독립2환경 검증. 게시 SHA 36419ac의 원격 Tests4matrix 각84passed6skipped·pipcheck 및 HACS/Hassfest 모두 독립 성공 확인. 원격 current Python3.14.8/HA2026.10.2/플러그인0.13.373, 최소 Python3.13.16/HA2025.2.0/플러그인0.13.210; 네 조합 imagespec[datamatrix]1.1.0/blesession0.9.0 실제 확인. 중앙 종료보고8d4348e 및 체크리스트/STANDARDS 마감 문서8093cbb main 반영 완료. 구현36419ac의 성공과 별개로 문서 최종 SHA8093cbb의 Tests4matrix·lint2와 Validate HACS/Hassfest도 독립 성공 확인. 적용 필수 PASS/N/A·현재 예외/TODO 없음. 실물·새 프록시 보드·HA UI 미검증 | 2026-10-17 / 조율 root · 구현 catprinter_implementation / catprinter_docs · 독립 리뷰 review_catprinter |
| [hass-cyx-rgb-led](https://github.com/eigger/hass-cyx-rgb-led) / `master` | 적용 제외 | — | 2026-10-17 사용자 명시 | 사용자 요청으로 공통화 대상에서 제외. 별도 요청 전 수정하지 않음 | 2026-10-17 / 미배정 |
| [hass-divoom](https://github.com/eigger/hass-divoom) / `master` | 적용 제외 | — | 2026-10-17 사용자 명시 | 사용자 요청으로 공통화 대상에서 제외. 별도 요청 전 수정하지 않음 | 2026-10-17 / 미배정 |
| [hass-esphome-ota](https://github.com/eigger/hass-esphome-ota) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-garage](https://github.com/eigger/hass-garage) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-gicisky](https://github.com/eigger/hass-gicisky) / `master` | 적용 제외 | — | GitHub archived 상태 확인 | hass-ble-esl로 이전. 별도 요청 전 이관 대상에서 제외 | 2026-10-17 / 미배정 |
| [hass-icscale](https://github.com/eigger/hass-icscale) / `main` | 진행 중 | tests/components/icscale 이전·공통 CI(current 3.14/HA2026.10.2, 정확한 최소 3.13/HA2025.2.0, blesession 하한 모드)·dependabot·영문/한글 README·동적 Usage·docs 분리·진입 지침 적용. 지원 최소 HA 2025.2.0 유지. 소스 변경은 ruff format뿐 | 기준 `78d242092eac732a1af48770e77e3f51e566c6c2` · [구현 main 커밋](https://github.com/eigger/hass-icscale/commit/4350ddff1e18dc772168e7c842e9e2c3713d1204) · [체크리스트](https://github.com/eigger/hass-icscale/blob/4350ddff1e18dc772168e7c842e9e2c3713d1204/ADOPTION_CHECKLIST.md) · [Tests](https://github.com/eigger/hass-icscale/actions/runs/39036976401) · [Validate](https://github.com/eigger/hass-icscale/actions/runs/39036976389) | PR #17 스쿼시 병합, main push의 Tests·Validate 성공. 로컬 current Python3.14.5/HA2026.10.2/플러그인0.13.373 및 최소 Python3.13.14/HA2025.2.0/플러그인0.13.210 각 58passed. 독립 리뷰는 Opus 서브 에이전트(지적 반영, 수정 후 재검증은 미수행). 남음: config_flow·migration 회귀 테스트(TEST-07), HA-01~13 코드 구조 점검, 구현 서브 에이전트 위임 예외(GOV-05). 실물 미검증 | 2026-10-17 / 조율 root · 구현 root · 독립 리뷰 Opus 서브 에이전트 |
| [hass-jaalee](https://github.com/eigger/hass-jaalee) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-kibble](https://github.com/eigger/hass-kibble) / `master` | 완료 | Core 대응 구조·실제 HA 테스트·공통 CI·로컬 brand 유지. 영어 기본 README.md·README.ko.md 상호 연결, 사전 조회 없는 동적 Usage, 간결한 메인·상세 docs 분리, 실제 Issues/Discussions·LICENSE 연결 반영. 지원 최소 HA 2025.3.0 / Python 3.13 / 플러그인 0.13.221, current HA 2026.10.2 / Python 3.14 / 플러그인 0.13.373 유지 | 기준 `7528a90b483a6740c0b1bdd9176f3e33355eb385` · [후속 구현 커밋](https://github.com/eigger/hass-kibble/commit/ed37181b20a82e5d88525509741fdd43217f2bc0) · [체크리스트](https://github.com/eigger/hass-kibble/blob/ed37181b20a82e5d88525509741fdd43217f2bc0/ADOPTION_CHECKLIST.md) · [최종 Tests](https://github.com/eigger/hass-kibble/actions/runs/39035536859) · [최종 Validate](https://github.com/eigger/hass-kibble/actions/runs/39035536869) · 이전 채택 [PR #8](https://github.com/eigger/hass-kibble/pull/8) | 후속 구현 ed37181의 기본 브랜치 반영 및 해당 SHA의 최종 원격 Tests·Validate·체크리스트 독립 검증 완료. current Python 3.14.8 / HA 2026.10.2 / 플러그인 0.13.373: 31 passed (1.19s), minimum Python 3.13.16 / HA 2025.3.0 / 플러그인 0.13.221: 31 passed (1.40s). 두 환경 pip check·HACS 9개·Hassfest PASS. 현재 필수 TODO·예외 없음. 실서버·실기기·HA UI 표시 미검증은 별도 한계로 유지 | 2026-10-17 / 조율 root · 구현 kibble_readme_usage_fix · 독립 리뷰 review_usage_language_fix |
| [hass-kma](https://github.com/eigger/hass-kma) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-kocom-smarthome](https://github.com/eigger/hass-kocom-smarthome) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-lywsd02](https://github.com/eigger/hass-lywsd02) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-magic-caster-wand](https://github.com/eigger/hass-magic-caster-wand) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-marklife](https://github.com/eigger/hass-marklife) / `main` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-melk-light](https://github.com/eigger/hass-melk-light) / `master` | 미착수 | — | 미등록 | 현황 점검·체크리스트 작성 | 2026-10-17 / 미배정 |
| [hass-minibig](https://github.com/eigger/hass-minibig) / `main` | 진행 중 | Core 대응 구조·실제 HA 테스트·공통 CI·blesession 하한·영문/한글 README·동적 Usage·기기별 Bluetooth 문서·진입 지침 적용 착수. 기존 지원 최소 HA 2025.8.0·통합 0.3.0·blesession>=0.9.0 보존 | 기준 `b1c80cf2c4bf8b4bc4e3556409ad948b7f850ea0` · 시작 대상 `c45775cf2179ae052fa0b1a47543ada91807f50e` | 차이 점검·체크리스트 작성·구현·독립 실제 HA 최소/current 검증 및 원격 CI 대기. 실물·새 프록시 보드·HA UI는 별도 미검증 | 2026-10-17 / 조율 root · 구현 minibig_implementation / minibig_docs · 독립 리뷰 minibig_review |
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
