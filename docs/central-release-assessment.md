# 중앙 표준의 릴리즈 단위 관리 검토

조사일: **2026-10-25 (Asia/Seoul)**. 결론은 **전환 가능**입니다. 중앙의 규칙·템플릿·도구·CI를 하나의 SemVer 릴리즈로 묶고, 통합은 검토한 **정확한 immutable release 태그 `vX.Y.Z`**를 채택하는 방식을 목표로 권고합니다. 실행·감사 증거에는 해당 태그가 가리키는 전체 SHA를 계속 보존합니다. 과도기에는 릴리즈 이름을 채택 단위로 사용하면서 실행 참조는 그 릴리즈의 SHA로 유지할 수 있습니다.

이 문서는 조사·설계 검토이며 정책 변경이나 전환 완료 기록이 아닙니다. 현행 GOV-02와 AGENTS.md는 중앙 태그·GitHub Release 생성을 금지합니다. 이번 검토에서는 태그·Release·PR을 생성하거나 중앙 정책·통합 파일을 변경하지 않았습니다.

## 조사 기준과 범위

- 중앙 원격 기본 브랜치 `main`: [`d8e1bccb729e057f2d37ace13c339743dcfdebac`](https://github.com/eigger/hass-repo-standards/tree/d8e1bccb729e057f2d37ace13c339743dcfdebac).
- 로컬 작업 시작 HEAD: `0ec31111a81b0ee5702f1d8a17f03616a10a5db6`. 로컬보다 원격이 앞서 있어 **원격 snapshot을 구현 계약 판단의 기준**으로 사용했습니다. 기존 로컬 변경은 보존했습니다.
- GitHub `eigger`의 `hass*` 리포 **30개**를 확인했습니다. 중앙 1개, HA 통합 25개, 기타 유형 4개입니다. 각 기본 브랜치의 HEAD를 API로 읽고 그 **정확한 SHA의 source archive**를 조사했습니다. 서로 다른 시각에 읽은 개별 리포 snapshot이며 GitHub 전체의 원자적 snapshot은 아닙니다.
- 조사 대상 텍스트 확장자는 `.md`, `.yml`, `.yaml`, `.json`, `.py`, `.sh`, `.toml`, `.txt`이며 파일당 2MB 이내입니다. `custom_components/<domain>/manifest.json`으로 통합을 식별하고 중앙 이름·`standards-ref`를 검색했습니다. 바이너리나 이 범위 밖 파일까지 무참조를 입증한 것은 아닙니다.
- [조사 증거 JSON](central-release-inventory.json)에 대상 커밋·파일·행과 참조를 보존합니다. 코드 검색 결과만으로 개수를 확정하지 않고 source snapshot에서 재집계했습니다.
- 중앙 `GET /repos/eigger/hass-repo-standards/releases`와 `/tags`는 조사 시점 모두 빈 배열이었습니다. 중앙 immutable release 설정·Actions 정책의 허용 여부와 실제 태그 실행은 아직 검증하지 않았습니다.

사용자가 언급한 19개와 달리 현재 원격에서 중앙을 참조하는 HA 통합은 **22개**입니다. 그중 **19개는 중앙 `ca740d8`**, 나머지 **3개는 `4ccbffa`**를 사용합니다. 이는 현재 두 그룹의 개수이며, 과거의 “19개”와 동일한 모집단이었다고 단정하지 않습니다. `hass-coolled` 같은 로컬 별칭 checkout은 별도 원격 리포로 중복 집계하지 않았습니다.

중앙 참조가 발견되지 않은 통합은 `hass-gicisky`(archived), `hass-divoom`, `hass-cyx-rgb-led`입니다. 기타 유형은 `hass-imagespec-card`, `hassble-android`, `hassble-config`, `hassio-apps`입니다. 중앙 현황표의 채택 상태와 이번 실제 참조 존재 여부는 별개이며, 참조 발견을 전체 표준 채택 완료로 해석하지 않습니다.

## 통합별 현재 실행 참조

아래 `uses` 수는 workflow YAML의 중앙 reusable workflow와 composite action 호출 **출현 횟수**입니다. matrix가 확장하는 실제 job 수나 문서 링크 수가 아닙니다. 중앙 SHA 약칭은 다음 전체 값입니다.

- `ca740d8`: `ca740d88b32fa5dcbc94c41fce2908450c76ed50`
- `4ccbffa`: `4ccbffa9af618b14d1a32a9939cbf1fcee6cb7a0`

| 통합 / 조사 소스 | 기본 브랜치 | 조사 대상 전체 커밋 | 중앙 실행 SHA | uses 수 |
|---|---|---|---|---:|
| [hass-atflee](https://github.com/eigger/hass-atflee/tree/8512682c776cdfa9095187410723e9118aa9b133) | `master` | [`8512682c776cdfa9095187410723e9118aa9b133`](https://github.com/eigger/hass-atflee/commit/8512682c776cdfa9095187410723e9118aa9b133) | `ca740d8` | 6 |
| [hass-ble-esl](https://github.com/eigger/hass-ble-esl/tree/6eff6d8d9baa1ffed2f58ef0097dfffe82f24d26) | `main` | [`6eff6d8d9baa1ffed2f58ef0097dfffe82f24d26`](https://github.com/eigger/hass-ble-esl/commit/6eff6d8d9baa1ffed2f58ef0097dfffe82f24d26) | `ca740d8` | 7 |
| [hass-ble-led-sign](https://github.com/eigger/hass-ble-led-sign/tree/c58a5b6481a7782ed4b602284a301974c9ac8b6c) | `master` | [`c58a5b6481a7782ed4b602284a301974c9ac8b6c`](https://github.com/eigger/hass-ble-led-sign/commit/c58a5b6481a7782ed4b602284a301974c9ac8b6c) | `ca740d8` | 6 |
| [hass-catprinter](https://github.com/eigger/hass-catprinter/tree/24ac52cf77733ae6c1e5e868e7b17f158316cb9d) | `main` | [`24ac52cf77733ae6c1e5e868e7b17f158316cb9d`](https://github.com/eigger/hass-catprinter/commit/24ac52cf77733ae6c1e5e868e7b17f158316cb9d) | `4ccbffa` | 8 |
| [hass-esphome-ota](https://github.com/eigger/hass-esphome-ota/tree/6bf4650bc08fb97633e250abe4af601f3987fffd) | `main` | [`6bf4650bc08fb97633e250abe4af601f3987fffd`](https://github.com/eigger/hass-esphome-ota/commit/6bf4650bc08fb97633e250abe4af601f3987fffd) | `ca740d8` | 4 |
| [hass-garage](https://github.com/eigger/hass-garage/tree/d4431e34ee19419dff1130c35f094d19769b88b8) | `master` | [`d4431e34ee19419dff1130c35f094d19769b88b8`](https://github.com/eigger/hass-garage/commit/d4431e34ee19419dff1130c35f094d19769b88b8) | `ca740d8` | 5 |
| [hass-icscale](https://github.com/eigger/hass-icscale/tree/44af64e18b4eeedd2530c3c075deeb060033fd35) | `main` | [`44af64e18b4eeedd2530c3c075deeb060033fd35`](https://github.com/eigger/hass-icscale/commit/44af64e18b4eeedd2530c3c075deeb060033fd35) | `ca740d8` | 6 |
| [hass-jaalee](https://github.com/eigger/hass-jaalee/tree/9dcd8ff6ec60010da738cd5f703b86d112e900c5) | `master` | [`9dcd8ff6ec60010da738cd5f703b86d112e900c5`](https://github.com/eigger/hass-jaalee/commit/9dcd8ff6ec60010da738cd5f703b86d112e900c5) | `ca740d8` | 5 |
| [hass-kibble](https://github.com/eigger/hass-kibble/tree/1865b929150e2b0585e23b6501d348ea9be5d6e6) | `master` | [`1865b929150e2b0585e23b6501d348ea9be5d6e6`](https://github.com/eigger/hass-kibble/commit/1865b929150e2b0585e23b6501d348ea9be5d6e6) | `4ccbffa` | 5 |
| [hass-kma](https://github.com/eigger/hass-kma/tree/e37a40d20a2607b496a09895bd06e83e684b2509) | `main` | [`e37a40d20a2607b496a09895bd06e83e684b2509`](https://github.com/eigger/hass-kma/commit/e37a40d20a2607b496a09895bd06e83e684b2509) | `ca740d8` | 5 |
| [hass-kocom-smarthome](https://github.com/eigger/hass-kocom-smarthome/tree/8bf0798c956185d4478d5849fd0004ded18204f6) | `main` | [`8bf0798c956185d4478d5849fd0004ded18204f6`](https://github.com/eigger/hass-kocom-smarthome/commit/8bf0798c956185d4478d5849fd0004ded18204f6) | `ca740d8` | 5 |
| [hass-lywsd02](https://github.com/eigger/hass-lywsd02/tree/7b1bc88feb2eac8f296eed44f018306a63f581f1) | `main` | [`7b1bc88feb2eac8f296eed44f018306a63f581f1`](https://github.com/eigger/hass-lywsd02/commit/7b1bc88feb2eac8f296eed44f018306a63f581f1) | `ca740d8` | 5 |
| [hass-magic-caster-wand](https://github.com/eigger/hass-magic-caster-wand/tree/6733342b710d59557409257ebef71ae1248fdee8) | `master` | [`6733342b710d59557409257ebef71ae1248fdee8`](https://github.com/eigger/hass-magic-caster-wand/commit/6733342b710d59557409257ebef71ae1248fdee8) | `ca740d8` | 6 |
| [hass-marklife](https://github.com/eigger/hass-marklife/tree/6f2e522ddae8af42e99816675a8fb44d6bff2157) | `main` | [`6f2e522ddae8af42e99816675a8fb44d6bff2157`](https://github.com/eigger/hass-marklife/commit/6f2e522ddae8af42e99816675a8fb44d6bff2157) | `4ccbffa` | 6 |
| [hass-melk-light](https://github.com/eigger/hass-melk-light/tree/3a74ba19cb69d0c9645aae0bef05b67167594504) | `master` | [`3a74ba19cb69d0c9645aae0bef05b67167594504`](https://github.com/eigger/hass-melk-light/commit/3a74ba19cb69d0c9645aae0bef05b67167594504) | `ca740d8` | 6 |
| [hass-minibig](https://github.com/eigger/hass-minibig/tree/b3919728481a6572bc396eb500cad0cee84f0088) | `main` | [`b3919728481a6572bc396eb500cad0cee84f0088`](https://github.com/eigger/hass-minibig/commit/b3919728481a6572bc396eb500cad0cee84f0088) | `ca740d8` | 8 |
| [hass-niimbot](https://github.com/eigger/hass-niimbot/tree/19134bcc151a8bd3cfa91138be347b23660eefff) | `master` | [`19134bcc151a8bd3cfa91138be347b23660eefff`](https://github.com/eigger/hass-niimbot/commit/19134bcc151a8bd3cfa91138be347b23660eefff) | `ca740d8` | 6 |
| [hass-omron](https://github.com/eigger/hass-omron/tree/cab86f9e3a3a2af88371354c7012925722b56bed) | `master` | [`cab86f9e3a3a2af88371354c7012925722b56bed`](https://github.com/eigger/hass-omron/commit/cab86f9e3a3a2af88371354c7012925722b56bed) | `ca740d8` | 6 |
| [hass-opinet](https://github.com/eigger/hass-opinet/tree/a9c56e4944eae281e6b8add6e4938cd7da1f9836) | `main` | [`a9c56e4944eae281e6b8add6e4938cd7da1f9836`](https://github.com/eigger/hass-opinet/commit/a9c56e4944eae281e6b8add6e4938cd7da1f9836) | `ca740d8` | 7 |
| [hass-sip](https://github.com/eigger/hass-sip/tree/58dc25025684c4c26b42a2c32a13ffff1cef3529) | `main` | [`58dc25025684c4c26b42a2c32a13ffff1cef3529`](https://github.com/eigger/hass-sip/commit/58dc25025684c4c26b42a2c32a13ffff1cef3529) | `ca740d8` | 5 |
| [hass-vson](https://github.com/eigger/hass-vson/tree/eb247f689bba34371f641907a2453255cc16be56) | `master` | [`eb247f689bba34371f641907a2453255cc16be56`](https://github.com/eigger/hass-vson/commit/eb247f689bba34371f641907a2453255cc16be56) | `ca740d8` | 5 |
| [hass-ws-bridge](https://github.com/eigger/hass-ws-bridge/tree/e69db676934f5ac6f7e8083d07f5c1cbbc9dbedf) | `main` | [`e69db676934f5ac6f7e8083d07f5c1cbbc9dbedf`](https://github.com/eigger/hass-ws-bridge/commit/e69db676934f5ac6f7e8083d07f5c1cbbc9dbedf) | `ca740d8` | 5 |

22개 통합의 중앙 `uses` **127개**는 모두 full SHA로 고정되어 있습니다. 각 통합 안에서 이번에 발견한 중앙 `uses`는 위 한 SHA로 일치했습니다. 모든 CI 동작이나 전체 표준 정합성 검사를 통과했다는 의미는 아닙니다.

## SHA 고정이 사용되는 범위

| 종류 | 원격 조사 결과 | 릴리즈 전환 시 처리 |
|---|---|---|
| 재사용 Tests | `python-tests.yml` 47회 / 22개 통합 | 최소/current·별도 테스트 caller 전체를 같은 채택 릴리즈로 생성 |
| 재사용 Validate | `validate-integration.yml` 22회 / 22개 | workflow 참조와 standalone checker 버전 일치 |
| 의존성 업데이트 | `dependency-update.yml` 12회 / 12개 | 테스트·업데이트 검증의 중앙 도구 버전 함께 갱신 |
| 표준 정적 검사 | `actions/check-standards` 22회 / 22개 | 새 태그 계약을 이해하는 검사기를 먼저 중앙에 구현 |
| 통합 ZIP 배포 | `actions/release-zip` 22회 / 22개 | 배포 전용 중앙 기준 필드와 기존 통합 태그/manifest 검증 보존 |
| 직접 환경 구성 | `actions/python-environment` 2회 | `hass-ble-esl` browser 및 `hass-opinet` 최소 의존성 job도 범위에 포함 |
| workflow 입력 | `standards-ref` 59회 | `uses`와 함께 갱신; inputs 값은 Dependabot 자동 동기화를 가정하지 않음 |
| 채택 기록·메타데이터 | `STANDARDS.md`, `.hass-standards.json`, 체크리스트 | 현행 release/tag/resolved SHA 기록 추가; 과거 검증 증거 보존 |
| 문서·개발 명령 | CONTRIBUTING·README·docs·CHANGELOG의 중앙 URL 및 로컬 checkout 안내 | 현행 규칙 링크는 채택 릴리즈로 연결; 역사 링크는 유지 |

참조가 발견된 workflow 파일은 100개, 그 외 파일은 67개입니다. 숫자는 중앙 이름 또는 `standards-ref`가 발견된 파일만 셌으며 다른 의존성 선언까지 집계한 값이 아닙니다. 문서 URL에는 현재 CI와 다른 예전 SHA와 `main` 링크가 함께 있습니다. 현황판 같은 의도적인 live 링크, 현재 규칙 링크, 과거 검증 증거를 구분해 바꿔야 합니다.

특히 `hass-minibig/STANDARDS.md`에는 현재 `ca740d8`와 과거 `b1c80cf` 기록이 함께 있습니다. 단순히 문서에서 SHA 두 개를 찾았다는 이유로 현재 실행 버전이 둘이라고 판정하면 안 됩니다. 과거 ADOPTION_CHECKLIST·CHANGELOG의 성공 기록을 새 릴리즈 링크로 일괄 치환하면 그 검증의 대상이 바뀌므로 금지해야 합니다.

## 중앙 관리의 목적과 불합리한 비용 검토

중앙화의 목적은 여러 통합에서 같은 형식·CI·검증을 반복 작성하는 비용을 줄이고, 검토한 변경을 안전하게 배포하는 것입니다. 동시에 통합별 실제 기능·지원 최소·예외·회귀 검증은 보존해야 합니다. 이 기준에서 릴리즈 도입은 **검토할 변경 묶음과 갱신 횟수를 줄일 때** 효과가 있습니다. SHA를 버전 문자열로 바꾸는 것만으로 운영 비용이 줄지는 않습니다.

| 확인한 사실 / 위험 | 목적에 비춰 본 판단 | 권고 |
|---|---|---|
| 127개 `uses` + 59개 `standards-ref` 입력 + 채택 기록에 동일 기준을 반복 표기 | 실행 YAML 자체의 반복은 GitHub 정적 문법 제약이 있지만, 사람이 전부 맞추게 하는 운영은 비용과 누락 위험이 큼 | 기계가 읽는 채택 버전 원본 하나에서 refs·inputs·현행 기록을 생성하고 같은 렌더러로 검사 |
| 중앙은 main commit을 기준으로 관리하고 현황·통계·정책·실행 도구가 같은 이력에 존재 | 현황표만 바뀐 commit을 새 도구 채택으로 취급한다면 불필요한 22개 갱신이 생김 | 배포 대상 변경과 운영 기록 변경을 구분; 실행·채택 계약 영향이 있는 묶음만 release |
| 기본 표준 SHA와 별도 release ZIP SHA를 허용하는 계약 존재 | 부분 채택에는 유용하지만 사람이 두 기준의 의미를 판단·동기화해야 하면 복잡해짐 | 한 릴리즈를 기본값으로 두고 별도 배포 도구 버전은 명시적 부분 채택으로 기계 검증; 현재 이력은 보존 |
| 문서에 과거 검증 SHA, 현재 규칙 SHA, live `main` URL이 공존 | 모두 “최신화”하면 감사 증거가 손상되고, 모두 고정하면 현황 링크도 낡음 | 실행 도구 버전·채택 정책 버전·과거 증거·live 현황 링크의 역할을 계약에 명시 |
| 필수 정적 검사·템플릿이 중앙에 모여 있음 | 검사 강화가 기존 리포를 실패시키면 기능 코드 변경이 없어도 소비자에게 비호환 | release notes와 SemVer 영향 판정에 검사·템플릿 변경도 포함; 필수/권장 수준을 편의상 바꾸지 않음 |
| 중앙 현황표와 각 통합 체크리스트에 상세 증거가 함께 쌓임 | 같은 실행 내역을 여러 곳에서 유지하면 내용이 갈리고 현황표가 배포 변경보다 더 자주 바뀜 | 체크리스트를 상세 증거 원본으로 두고 중앙 표는 상태·기준·대상 commit·근거 링크·남은 일로 요약 |
| HACS/Hassfest 이미지와 패키지 index 등 외부 요소는 중앙 commit 밖에서 변함 | 중앙 release만으로 모든 CI 재현성을 보장한다는 운영 기대는 부정확 | 정기 Validate와 실제 설치 버전 기록 유지; 완전 재현이 필요할 때 별도 image digest·환경 lock 범위 검토 |
| 현재 참조 통합은 22개이나 사용자 전제는 19개 | 과거 숫자를 자동 배포 대상 목록으로 쓰면 대상 누락·확대 가능 | 실제 원격 인벤토리를 기준으로 조사 범위와 향후 적용 대상을 명시적으로 구분 |

두 번째 행은 **현행이 모든 중앙 commit마다 전체 통합을 갱신하도록 강제한다는 뜻이 아닙니다**. GOV-03과 채택 절차는 이미 영향 검토와 개별 리포의 명시적 채택 PR을 요구합니다. 여기서 지적한 불합리는 앞으로 릴리즈 자동화를 만들 때 현황·통계 변경까지 “업데이트 필요”로 계산하는 설계의 위험입니다.

SHA 고정 자체는 검토한 코드를 유지하기 위한 합리적인 안전장치입니다. 개선할 부분은 사람이 변경 검토·배포 단위까지 개별 commit으로 해석하고 여러 파일을 수동 동기화하는 부담입니다. 기본은 한 릴리즈 bundle로 운영하고 별도 배포 도구 버전은 실제 독립 수명주기가 필요한 경우로 한정하는 편이 낫습니다.

기준 갱신 때마다 전체 GOV 채택 절차를 처음부터 반복하도록 만들 필요도 없습니다. 기존 유효한 채택·예외를 보존하면서 해당 릴리즈가 바꾼 규칙과 영향 있는 동작을 재검증하고 필요한 회귀 검사를 수행하도록 제안합니다. 지원 최소 상향은 기존의 별도 명시적 사용자 승인 조건을 유지합니다. CI에 승인 대기를 추가하지 않습니다.

기계가 수집하는 실제 ref 인벤토리와 사람이 검증하는 채택 완료 판정도 분리해야 합니다. 이번 19개와 22개의 차이를 현황표 오류나 전체 완료의 근거로 삼지 않으며, 현황표는 실제 인벤토리를 연결하고 완료 판정의 증거를 요약하도록 권고합니다.

한 릴리즈가 모든 통합에 적합하다고 가정해 지원 최소를 올리거나, 새 검사에 맞추려고 없는 기능을 만들게 하는 것도 중앙화 목적과 맞지 않습니다. 릴리즈는 공통 도구의 배포 단위이며 통합 지원 범위 변경의 승인 수단이 아닙니다. 기존 예외·선택 기능·최소/current 검증은 각 리포의 실제 메타데이터로 유지해야 합니다.

운영상 권고하는 역할은 다음과 같습니다.

- **중앙 릴리즈**: 검토 가능한 규칙·템플릿·도구의 배포 묶음. 버전과 commit, 호환성·이관·검증 근거를 제공.
- **통합의 기계 판독 원본**: 채택 release와 resolved SHA, 필요할 때만 별도 배포 도구 버전, 적용 profile·승인 예외를 보유. 현재 `.hass-standards.json`과 중복되지 않게 기존 계약을 확장할지 먼저 결정.
- **생성된 workflow·현행 STANDARDS**: 위 원본을 사람이 검토하고 GitHub가 실행할 정적 형태로 표현. 수동 버전 편집을 정상 갱신 경로로 만들지 않음.
- **체크리스트·과거 기록**: 당시 대상 commit과 검증 결과를 보존. 새 릴리즈를 채택할 때 별도 갱신 증거를 추가.
- **중앙 현황표**: 전체 진행을 찾는 요약 인덱스. 다른 세션의 상세 결과를 재작성하는 추가 원본으로 만들지 않음.

이 역할 분리는 제안이며 현재 구현된 단일 버전 원본·자동 갱신 도구가 있다는 뜻은 아닙니다. 먼저 과도기 방식으로 릴리즈 채택 단위를 도입한 뒤, 반복 갱신을 줄이는 생성·검사 경로까지 구현해야 사용 목적에 맞는 개선이 됩니다.

## 관리 방식 비교

| 선택지 | 채택·실행 방식 | 판단 |
|---|---|---|
| 릴리즈 이름 + 실행 SHA | `v1.0.0`을 검토하고 `uses: …@<그 릴리즈 SHA> # v1.0.0` | 기존 실행 계약을 대부분 유지하는 과도기안. 사람은 릴리즈 단위로 갱신하지만 YAML에는 SHA가 남음 |
| 정확한 immutable release 태그 | `uses: …@v1.0.0`, resolved SHA 별도 기록 | **목표안**. 사용자가 원하는 버전 가독성과 고정 실행을 함께 제공; 중앙 도구 개편 필요 |
| 일반 exact 태그만 생성 | `uses: …@v1.0.0`, 태그 이동 방지 보장 없음 | 태그 이동 가능성이 있어 목표안의 보호를 제공하지 못함 |
| 이동 major/minor·branch | `@v1`, `@v1.2`, `@main`, 매 실행 latest 조회 | 중앙 변경이 검토 없이 전파될 수 있어 비권고 |

GitHub는 재사용 workflow에 SHA·release tag·branch 참조를 지원합니다. 다만 `jobs.<job_id>.uses`에는 context나 expression을 사용할 수 없으므로 `${{ vars.STANDARDS_VERSION }}` 같은 변수 하나로 모든 caller를 연결하는 설계는 사용할 수 없습니다. **설정 한 곳에서 정적인 workflow YAML을 생성·검사**하는 방식이 필요합니다. [공식 재사용 workflow 문서](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)

GitHub immutable release는 발행 후 연결 태그의 이동과 자산 변경을 막습니다. 릴리즈를 삭제한 뒤 같은 태그명을 재사용하는 것도 제한합니다. 일반 Git 태그와 immutable release를 구분해야 하며 “모든 태그는 가변이므로 릴리즈 참조가 불가능하다”는 결론은 맞지 않습니다. [공식 immutable release 설명](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)

정확한 release 태그와 이동 가능한 major/minor 태그도 구분해야 합니다. 이 중앙 리포에서는 **발행한 `vX.Y.Z`의 재지정·재사용을 금지**하고 수정은 새 버전으로 발행하도록 제안합니다. [공식 Actions 릴리즈 관리](https://docs.github.com/en/actions/how-tos/create-and-publish-actions/using-immutable-releases-and-tags-to-manage-your-actions-releases)

Workflow dependency lockfile은 별도 대안이지만 확인한 공식 문서에서는 Enterprise Cloud의 public preview입니다. 계정 지원 여부와 실제 실행을 확인하지 않았으므로 이번 설계의 필수 기반으로 삼지 않습니다. [공식 lockfile 안내](https://docs.github.com/en/actions/how-tos/secure-your-work/lock-workflow-dependencies)

## 중앙에서 변경해야 할 계약

아래는 원격 `d8e1bcc`의 구현을 기준으로 한 변경 범위이며, 구현 완료 목록이 아닙니다. 규칙 ID와 필수/권장 수준은 유지하고 해당 본문 계약을 개정해야 합니다.

| 영역 | 주요 파일 | 필요한 변경 |
|---|---|---|
| 관리 정책 | `AGENTS.md`, 양언어 README, `docs/adoption.md` GOV-01/02/03, `docs/ci.md` CI-05, `docs/releases.md`, 체크리스트 | 중앙 태그 금지 대신 immutable release 정책, 채택 단위·이관·release 기준·감사 SHA 정의 |
| 생성·채택 입력 | `scripts/manage_integration.py`, `scripts/standards/planning.py`, `schemas/integration-plan.schema.json` | 현재 full40 입력/HEAD 일치 계약에 release/tag와 resolved SHA를 구분해 추가. 기존 SHA 입력 호환 유지 |
| 계획 적용·복구 | `scripts/standards/apply.py`, 관련 schema·검증 | plan의 버전과 해석한 SHA를 고정하고 apply/recover에서 재검증. 같은 태그가 다른 commit으로 해석되면 중단 |
| 정적 정합성 | `scripts/check_integration.py`, `scripts/standards/validation.py`, `scripts/payload_documents.py`, `scripts/check_repository.py` | full40 정규식·ref 비교·중앙 템플릿 검사에 exact release 계약 추가. 태그 문자열뿐 아니라 기록한 SHA와의 결합을 검증 |
| 실행 도구 checkout | `.github/workflows/python-tests.yml`, `dependency-update.yml` 및 caller templates | `standards-ref` full40 전제와 별도 도구 checkout을 개편. caller 소스·최소/current 환경·경로 충돌 guard 유지 |
| 패키징 | `actions/release-zip/action.yml`, `scripts/build_release_zip.py`, release caller template | 중앙 도구 버전과 통합 자체 release tag를 구분. 기존 Git tree·manifest·asset 검증 보존 |
| 공통 템플릿·스킬 | `templates/integration/`의 STANDARDS·CHECKLIST·USAGE·caller, `skills/*` 및 참조 문서 | 릴리즈 선택 → resolved SHA 확인 → 계획 → 적용 → 검사로 같은 경로 사용 |
| 회귀 검사 | `tests/test_integration_contract.py`, planning/apply/scenarios/repository tests, release ZIP tests·workflow fixtures | 기존 SHA 입력, 새 태그, mismatched SHA·미발행/이동 태그 거부, 원자적 갱신, rollback을 실제 실행 |

현재 `validation.py`는 보통 `STANDARDS.md`의 검토 SHA와 중앙 `uses`·`standards-ref`의 일치를 검사합니다. 다만 **`Reviewed release standards SHA` 필드가 있으면 `release.yml`의 `actions/release-zip`만 별도 검토 SHA를 사용할 수 있습니다**. 이 기존 분리를 무시하고 무조건 한 SHA로 합치면 과거 채택 계약을 바꾸게 됩니다. 새 모델도 기본 표준 버전과 배포 전용 버전의 선택적 분리를 명시적으로 지원하거나 별도 이관해야 합니다.

중앙 reusable workflow 자체도 현재 `python-environment@d5dcaa03…`, `update-manifest@8e7b3b41…`처럼 과거 중앙 action SHA를 호출합니다. 외부 caller에 새 릴리즈 태그를 붙이는 것만으로 내부 action까지 같은 릴리즈 commit이 되지는 않습니다. 초기 릴리즈는 **검증한 내부 의존성 SHA 집합을 포함한 배포 구성**으로 기록할 수 있습니다. 내부 action도 같은 릴리즈 코드를 실행하게 개편한다면 caller checkout과 action source 경계를 보존하는 별도 구현·검증이 필요합니다.

GitHub의 최신 self-repository 문법인 `uses: $/actions/python-environment`는 같은 저장소의 action을 실행 중인 commit에서 참조하며 별도 checkout이 필요하지 않습니다. 따라서 내부 과거 SHA의 중복 관리를 줄일 **검증 후보**로 검토할 가치가 있습니다. 이는 아래의 `./actions/...` 문법과 다르며 GitHub Enterprise Server에서는 지원되지 않습니다. 현재 중앙의 actionlint·검사기 호환성, 실제 reusable workflow caller에서의 동일 commit 선택과 `github.action_path` 동작은 실행 검증하지 않았으므로 바로 적용 가능한 해법으로 확정하지 않습니다. 기존 내부 SHA 구성의 보존은 초기 호환 전략이며 영구 목표가 아닙니다. [공식 self-repository action 안내](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/find-and-customize-actions)

특히 reusable workflow에서 단순히 `uses: ./actions/...`로 변경하면 기존 checkout인 통합 소스를 읽게 됩니다. 중앙 action은 `github.action_path`, 중앙 도구는 별도 예약 경로를 유지해야 하며 caller 파일을 덮으면 안 됩니다.

태그 지원을 full40 정규식 완화만으로 구현하면 안 됩니다. 제안하는 입력은 `release: vX.Y.Z`와 `resolved_sha: <full40>`이며, 중앙이 발행한 release인지·immutable인지·정확한 commit인지 확인하는 경계를 마련해야 합니다. CI의 offline 검사와 원격 release 확인은 구분하고, 네트워크 확인 실패를 성공이나 `main` fallback으로 처리하지 않아야 합니다. 이 필드명은 설계 예시이며 현재 CLI/스키마에 존재하는 기능이 아닙니다.

## 릴리즈·갱신 운영안

1. **배포 범위를 정의합니다.** 규칙·템플릿·schema·skills·scripts·actions·reusable workflow를 하나의 릴리즈로 묶습니다. 현황표·통계의 단순 갱신마다 배포하지 않되, 채택 판정이나 검사 동작에 영향을 주는 변경은 릴리즈 대상에 포함합니다.
2. **SemVer를 적용합니다.** 입력·출력·필수 검사·생성 결과에 비호환이 생기면 major, 기존 caller를 보존하는 기능은 minor, 호환 수정은 patch로 분류합니다. 검사 강화로 기존 채택 리포가 실패하는 경우도 영향 분석에 포함합니다. 중앙 버전과 통합의 manifest.version·HA 지원 최소는 독립입니다.
3. **같은 commit을 검증하고 발행합니다.** 새 중앙 release CI는 check_repository·단위 회귀·actionlint·workflow fixtures와 실제 caller smoke 검증 증거를 특정 commit에 연결합니다. draft의 자산을 먼저 완성하고 immutable release를 발행합니다. 초기 `v1.0.0`은 버전 예시이며 이번에 검증·발행한 값이 아닙니다.
4. **릴리즈 내용에 이관 정보를 제공합니다.** 버전→commit, 계약 버전, 내부 action 의존성, 변경 규칙 ID·영향, 필요한 caller 변경, 알려진 한계·검증 범위·CI 링크를 기록합니다. `latest` 표시는 채택 버전을 바꾸는 근거로 사용하지 않습니다.
5. **통합마다 하나의 갱신 PR을 만듭니다.** 생성기가 현재 버전을 읽고 대상 release의 refs·모든 `standards-ref`·현행 STANDARDS·관리 metadata·현재 문서 링크를 함께 변경합니다. 관리 범위 밖 본문·회귀 테스트·기존 예외·지원 최소·과거 증거를 보존합니다. 검토·병합 전 적용하지 않습니다.
6. **파일럿 후 확대합니다.** 먼저 SHA 입력과 새 태그 입력을 함께 지원하는 중앙을 준비하고, imagespec/blesession 및 ZIP 배포가 있는 대표 통합과 일반 HA 통합에서 실제 검증합니다. 최소/current가 다르면 각각 실행합니다. 이후 나머지 통합으로 순차 확대하며 기본 브랜치 커밋의 CI로 완료를 판정합니다.
7. **문제가 있으면 caller를 이전 릴리즈로 되돌립니다.** 태그를 이동하거나 기존 자산을 교체하지 않고 버전·resolved SHA·inputs를 함께 되돌리는 PR을 사용합니다. 잘못된 릴리즈의 제한을 안내하고 새 patch/major를 발행합니다.

Dependabot은 GitHub Actions `uses` 갱신에 활용할 수 있지만 `with.standards-ref`, STANDARDS, 메타데이터, 문서 링크까지 원자적으로 갱신한다고 가정하면 안 됩니다. 관련 중앙 참조를 묶는 설정만으로 이 결합이 보장되지도 않습니다. **릴리즈 갱신 생성기 또는 Dependabot 제안을 완성하는 별도 검증된 도구**가 필요하며, 현재 제공되는 기능으로 보고하지 않습니다. 외부 action SHA의 보안 갱신 정책은 중앙 release 태그 도입과 분리해 유지합니다.

Immutable release 설정은 우선 **중앙 리포에 한정**합니다. 기존 통합의 `release.yml`은 `release.published` 후 ZIP asset을 올리는 방식이므로 통합 리포까지 무조건 immutable을 켜면 자산 업로드와 충돌할 수 있습니다. 통합 릴리즈의 배포 흐름을 바꾸는 작업은 이번 중앙 버전 관리 전환과 별도 범위입니다.

## 전환 완료 조건과 이번 검토의 한계

- 중앙 정책 개정과 exact release·resolved SHA 모델, 구형 SHA caller 호환이 구현되어야 합니다.
- 릴리즈 후보의 실제 검증 결과와 CI 링크가 있어야 하고, 발행한 release의 immutable 상태·tag commit을 확인해야 합니다. 각 리포·조직의 full-SHA 강제 정책과 태그 참조의 호환성도 실제 확인해야 하며, 태그를 허용하지 않으면 릴리즈 SHA 방식으로 유지합니다.
- 생성·검사·apply/recover가 같은 release를 사용하고, `uses`·inputs·기록의 불일치 및 태그 이동을 거부해야 합니다.
- 대표 통합에서 기존 회귀·최소/current HA·imagespec 계약·ZIP 경계가 보존되는지 검증한 후 확대해야 합니다.
- 각 통합의 갱신은 실제 기본 브랜치 반영과 해당 commit 검증 뒤 완료로 기록해야 합니다. 이전 SHA 유지 통합은 미전환으로 남겨야 합니다.

이번 조사로 확인한 것은 **원격 파일의 참조 현황과 중앙 구현의 전환 영향**입니다. 새 릴리즈 발행, 태그 caller 실행, 릴리즈 갱신 생성기, 실제 HA·기기·ZIP 배포 검증은 수행하지 않았습니다. 따라서 현재 가능한 결론은 “릴리즈 단위 전환을 권고하며 위 계약을 함께 구현해야 한다”이며, “이미 릴리즈 참조로 동작한다”가 아닙니다.
