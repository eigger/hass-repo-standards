# 템플릿·스킬 구현 검증 기록

2026-10-19. [작업지시서](template-skill-tasks.md)의 중앙 도구 구현 결과를 기록합니다. 개별 통합의 채택 결과나 지원 최소/current HA 검증을 대신하지 않습니다.

## 검증 대상과 단계

설계 baseline은 `77c279406d7b10e13cc72fa25495a6b648b9d98f`입니다. T1은 `1968bbf446e665ab6b496bc62227bf1620d6fd1c`로 커밋하고 [PR #2](https://github.com/eigger/hass-repo-standards/pull/2)에 제출했으며, 해당 커밋의 [원격 CI](https://github.com/eigger/hass-repo-standards/actions/runs/39194455236) 네 검사가 모두 성공했습니다. 설계 [PR #1](https://github.com/eigger/hass-repo-standards/pull/1)은 merge commit `87ae6450ebc3e2d5ad7a5b835f9716eab94ff1a0`, T1 PR #2는 `0fd0dee351965f46b960903201d046f573465d02`로 main에 반영했습니다.

T2는 실제 커밋 `a1e37401533e65651f910d498f9b3a2d21764b8b`의 [PR #3 CI](https://github.com/eigger/hass-repo-standards/actions/runs/39196264296) 네 검사가 모두 성공한 뒤 merge commit `89e842466c8970be1c17df84e960c0d355409fb9`로 main에 반영했습니다. 해당 [main CI](https://github.com/eigger/hass-repo-standards/actions/runs/39196437890) 네 검사도 모두 성공했습니다.

T3는 실제 커밋 `419c23441cd8b4e6e37ceca6df0c0493b199d7b0`의 [PR #4 CI](https://github.com/eigger/hass-repo-standards/actions/runs/39198455037) 네 검사가 모두 성공한 뒤 merge commit `2433321f4d1f7eba6b3bc3646aa3ba0b251dc419`로 main에 반영했습니다. 해당 [main CI](https://github.com/eigger/hass-repo-standards/actions/runs/39198603979) 네 검사도 모두 성공했습니다. 현재 T4 검증 대상은 이 main 커밋 위의 작업 트리 변경분이며 독립 코드 검증을 완료했습니다. 최종 커밋·원격 CI는 대기 중이며 이전 단계 결과를 T4 검증으로 재사용하지 않습니다.

| 단계 | 구현·검증 상태 | 남은 작업 |
|---|---|---|
| T1 | 계약·스키마·공통 모듈 구현, 독립 코드/문서 검증·커밋 CI 네 검사 성공·main 병합 | 후속 단계와 별도 기록 |
| T2 | 읽기 전용 inspect/plan·조사·변경 계획 구현, 독립 코드/문서 검증·커밋/main CI 각 네 검사 성공·main 병합 | 후속 단계와 별도 기록 |
| T3 | 새 작성 기반·apply·recover 구현·독립 코드/문서 검증·PR/main CI 각 네 검사 성공·main 병합 | 후속 단계와 별도 기록 |
| T4 | 생성물 검사·중앙 계약·스키마·자산 무결성 연결 구현·독립 코드/문서 검증 완료 | 커밋/CI 근거 확정 |
| T5 | TODO | 두 스킬·설치 및 실행 안내·동작 검증 |
| T6 | TODO | 중앙 생성·갱신 fixture와 별도 범위의 실제 통합 검증 |

T1은 계약 44개 중 기존 원본 available 21개와 미작성 자산 pending 23개를 구분했습니다. T3는 작성 자산 18개와 빈 `custom_components/__init__.py` 패키지 marker를 추가해 총 45개·available 40개·pending 5개입니다. marker는 기존 빈 테스트 init 원본을 재사용하고 create_only로 기존 파일을 보존합니다. available은 원본이 존재한다는 뜻이며 실제 기기 동작·fixture·검증 미완료는 renderer의 pending으로 별도 반환합니다. CLI에는 T2 inspect/plan과 T3 apply/recover가 있습니다. 외부 통합 수정·지원 최소 변경·스킬 설치·workflow 수동 실행은 수행하지 않았습니다.

## 현재 사용할 수 있는 T1 API

저장소 루트에서 실행합니다. 다음 코드는 계약을 읽고 검증할 뿐 대상 파일을 생성하거나 변경하지 않습니다.

```bash
PYTHONPATH=scripts python3 -c "from standards.contract import load_contract; print(len(load_contract()['records']))"
python3 -m unittest discover -s tests -p test_standards_contract.py -v
```

`standards.contract.validate_input(data)`는 출처를 포함한 신규 입력을, `validate_document(data, "inventory")`와 `validate_document(data, "plan")`은 조사·계획 CLI 산출물의 스키마를 검증합니다. 실제 명령과 sourced 입력 예시는 [사용 안내](template-skill-usage.md)에 있습니다. T3 계획에는 필수 `target_identity.root_exists`가 추가되므로 이전 T2 계획은 새 검토 SHA에서 재생성해야 합니다.

## 실행 환경과 baseline

독립 검증은 구현 담당 환경과 분리한 Linux WSL snapshot에서 Python 3.14.4로 실행했습니다. 실제 HA 회귀용 별도 환경 `/home/eigger/hass-standards-review-ha-s3tDc4/.ha-venv`에는 HA 2026.10.2, pytest-homeassistant-custom-component 0.13.373, imagespec 1.0.1을 설치했습니다. 이 조합은 중앙 payload 회귀 검증용이며 특정 통합의 지원 최소를 선언하거나 검증한 결과가 아닙니다.

| 대상 | 명령·검사 | 결과 |
|---|---|---|
| baseline `77c2794` | `python3 -m unittest discover -s tests -v` | 60개 중 도구 54개 성공, HA 환경이 필요한 6개 skip; 전체 실행 성공으로 기록하지 않음 |
| baseline `77c2794` | `python3 scripts/check_repository.py` | 문서 35개·workflow 7개 검사 성공 |
| baseline `77c2794` | `python3 -m ruff check .`, `python3 -m ruff format --check .` | 성공; format 대상 61개 |
| 별도 HA 환경 | `uv pip check --python <HA 환경>/bin/python` | 155개 설치 패키지 환경 의존성 충돌 없음 |

## T1 변경분 검증

| 담당·범위 | 명령·검사 | 현재 결과 |
|---|---|---|
| 구현 담당, 최종 optional remote 입력 포함 | `python3 -m unittest discover -s tests -p test_standards_contract.py -v` | 신규 19개 성공 |
| 구현 담당, 같은 변경분 | `python3 -m ruff check .`, `python3 -m ruff format --check .` | 성공; format 대상 67개 |
| 독립 검증, optional remote 입력 추가 직전 snapshot | 전체 도구 회귀와 별도 실제 HA 회귀 | 도구 72개와 HA 6개 모두 실행·성공; 최종 변경 검증으로 재사용하지 않음 |
| 독립 검증, 같은 snapshot | `python3 scripts/check_repository.py` | 문서 35개·workflow 7개 검사 성공; 문서 갱신 전 결과 |
| 독립 검증, 최종 optional remote 입력 포함 | `python3 -m unittest discover -s tests -v` | 79개 중 도구 73개 성공, HA 환경용 6개 skip; 아래 별도 HA 환경에서 6개 모두 실행 |
| 독립 검증, 같은 snapshot | 별도 실제 HA 회귀 | 6개 모두 성공, 12.308초; 도구 결과와 합쳐 서로 다른 79개 테스트 실행 성공 |
| 독립 검증, 같은 snapshot | `python3 scripts/check_repository.py` | 문서 35개·workflow 7개 검사 성공; 문서 갱신 전 결과 |
| 독립 검증, 같은 snapshot | `python3 -m ruff check .`, `python3 -m ruff format --check .` | 성공; format 대상 67개 |
| 독립 검증, 별도 parity 환경 | jsonschema 4.26.0의 `Draft202012Validator`와 자체 검증기 비교 | 127개 corpus의 허용/거부 결과 일치; 프로젝트 의존성 추가 없음 |
| 독립 검증, 최종 snapshot에 문서 6개 반영 | `python3 scripts/check_repository.py`, `git diff --check` | 문서 36개·workflow 7개 검사 성공, diff 검사 종료 코드 0; 코드 14개 fingerprint 불변·문서 필수 지적 없음 |

최종 독립 코드 snapshot은 `/home/eigger/hass-standards-review-t1-final-qdeMCv`입니다. 이 snapshot의 `final-fingerprints.txt`는 코드 파일 14개의 SHA-256을 기록하며 manifest 자체의 SHA-256은 `53c2daac819925fec9b58c10ea63a309a5d79f50ac7ee79dcc131e08a439d96e`입니다. 이 값은 Git 커밋 SHA가 아닙니다. 독립 리뷰에서 관리 경계·계약 메타데이터·numeric minimum·optional remote 관련 보완을 재검증했으며 미해결 필수 지적은 없습니다.

아래는 해당 snapshot에서 실행한 정확한 명령입니다. parity 비교는 별도 환경의 일회성 reviewer 실험이며 저장소에 추가한 자동 테스트가 아닙니다.

```bash
cd /home/eigger/hass-standards-review-t1-final-qdeMCv
.venv/bin/python -m unittest discover -s tests -v > tools-tests-final.log 2>&1
.venv/bin/python scripts/check_repository.py
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
/home/eigger/hass-standards-review-ha-s3tDc4/.ha-venv/bin/python -m unittest discover -s tests -p test_payload_runtime.py -v > ha-tests-final.log 2>&1
/home/eigger/.local/bin/uv pip check --python /home/eigger/hass-standards-review-ha-s3tDc4/.ha-venv/bin/python
```

새 계약 테스트는 잘못된 버전·중복 대상·필수 입력 누락·지원하지 않는 조건·경로 이탈·스키마 허용/거부·라이브러리 네 조합과 기존 공개 renderer 일치를 검증합니다. T1 커밋의 원격 CI는 네 검사 모두 성공했고 실제 HA job은 1분 16초에 완료했습니다. workflow를 수동 실행하지 않고 PR CI 결과를 읽어 확인했습니다.

## T2 변경분 검증

| 담당·범위 | 명령·검사 | 결과 |
|---|---|---|
| 구현 담당, Windows | `python3 -m unittest discover -s tests -p test_integration_planning.py -v` | 신규 26개 중 25개 성공·symlink 1개 skip; 이 결과만으로 전체 실행 성공 처리하지 않음 |
| 구현 담당, 같은 변경분 | 계약 테스트·Ruff | T1 계약 19개 성공, Ruff check/format 성공·72개 파일 |
| 독립 검증, Linux snapshot | 전체 도구 회귀·별도 실제 HA 회귀 | 도구 99개와 HA 6개, 서로 다른 총 105개 모두 실행 성공; HA 6개 12.542초 |
| 독립 검증, 같은 snapshot | `python3 scripts/check_repository.py` | 문서 36개·workflow 7개 성공; 이번 T2 문서 갱신 전 결과 |
| 독립 검증, 같은 snapshot | `python3 -m ruff check .`, `python3 -m ruff format --check .` | 성공·72개 파일 |
| 독립 검증, 외부 jsonschema 비교 | 계획의 내장 입력·로컬 `$ref` 검사 | 25개 corpus 판정 일치·금지 참조 6개 거부·형제 type 제약 검증 성공 |
| 독립 검증, 깨끗한 임시 Git 저장소 | 실제 inspect/create plan CLI smoke | 반복 JSON 일치·입력 스냅샷 digest·대상 불변·대상 내부 출력 거부·수정된 중앙 자산 거부 확인 |
| 독립 검증, 최종 snapshot에 문서 7개 반영 | 사용 안내 JSON의 schema·fixture 비교, 저장소·diff 검사 | 입력 JSON schema와 fixture 정확 일치·문서 37개/workflow 7개 검사 성공·diff 검사 종료 코드 0·코드 6개 fingerprint 불변·문서 필수 지적 없음 |

최종 독립 코드 snapshot은 `/home/eigger/hass-standards-review-t2-3qFlgm`입니다. 코드 파일 6개의 fingerprint manifest SHA-256은 `eecc910b63f53264411f57f142de152aa36ecae648020a821655a976f827e4fd`이며 Git 커밋 SHA가 아닙니다. CLI smoke 산출물은 `/home/eigger/hass-t2-cli-smoke-tgym4a4s`에 기록했습니다. 독립 리뷰의 미해결 필수 지적은 없습니다. 임시 Git fixture는 배포 커밋이나 실제 통합 도입 근거가 아닙니다.

도구 환경은 Python 3.14.4·packaging 26.3·PyYAML 6.0.3·Ruff 0.17.1입니다. HA 환경은 T1의 HA 2026.10.2·플러그인 0.13.373·imagespec 1.0.1을 변경 없이 사용했습니다. 정확한 실행 명령은 다음과 같습니다.

```bash
cd /home/eigger/hass-standards-review-t2-3qFlgm
.venv/bin/python -m unittest discover -s tests -v > tools-tests.log 2>&1
.venv/bin/python scripts/check_repository.py
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
/home/eigger/hass-standards-review-ha-s3tDc4/.ha-venv/bin/python -m unittest discover -s tests -p test_payload_runtime.py -v > ha-tests.log 2>&1
```

## T3 변경분 검증

| 담당·범위 | 명령·검사 | 현재 결과 |
|---|---|---|
| 작성 기반 구현 담당, Windows Python 3.14.6 | `python -m unittest discover -s tests -p test_integration_scaffold.py -v`, 계약 테스트 | 초기 신규 7개·기존 계약 19개 성공; package marker 보완 후 신규 8개·계약 19개 성공 |
| 작성 기반 구현 담당, 같은 변경분 | 해당 파일 Ruff check/format·`git diff --check` | 성공 |
| 독립 검증, Linux 작성 기반 단독 | 신규 작성 기반 7개·기존 계약 19개 테스트 | 성공; apply/recover를 포함한 T3 전체 검증으로 재사용하지 않음 |
| 작성 기반 구현 담당, Windows | `python scripts/check_repository.py` | 기본 cp949 디코딩 오류; PYTHONUTF8=1 재실행은 기존 README 개행에 따른 header 보호 오류로 미통과 |
| 최종 독립 검증, Linux | 전체 도구 회귀·별도 실제 중앙 HA 회귀 | 도구 140개와 HA 6개, 서로 다른 146개 모두 실행 성공; 중앙 HA 6개 11.990초 |
| 최종 독립 검증, 같은 snapshot | 저장소 검사·Ruff check/format | 문서 37개·workflow 7개 검사 성공·Ruff 성공·77개 파일 |
| 최종 독립 검증, 깨끗한 임시 Git | 실제 CLI create→apply→동일 입력 adopt→recover→재recover | 추가 operations 0·복구와 반복 복구 성공 |
| 최종 생성 초안, 실제 HA | config flow 개별 실행 negative smoke | 실제 loader가 example을 로딩하고 의도한 TODO `NotImplementedError`에 도달·종료 코드 1; 완성 통합 성공 아님 |
| 최종 독립 검증, 문서 7개 반영 | 저장소·diff 검사 | 문서 37개/workflow 7개 검사 성공·diff 검사 종료 코드 0·코드 26개 fingerprint 불변·문서 필수 지적 없음 |

최종 독립 snapshot은 `/home/eigger/hass-standards-review-t3-final-1MjOtG`, 실제 CLI 산출물은 `/home/eigger/hass-t3-final-cli-smoke-476tqa1t`이며 negative 로그는 그 아래 `draft-ha-negative.log`입니다. `code-fingerprints.txt`에 기록한 코드 26개는 공유 작업 트리와 같고 manifest SHA-256은 `66ff41fd80b82b6bb02cb24ce8a05ec4c9afe517f037d50f1a8ee815da1280e8`입니다. 이 값은 Git 커밋 SHA가 아닙니다. 필수 미해결 지적은 없습니다. 초기 수정 전 143개 결과를 최종 검증에 재사용하지 않았습니다.

환경은 T1/T2와 같은 Python 3.14.4·packaging 26.3·PyYAML 6.0.3·Ruff 0.17.1, 별도 중앙 HA 2026.10.2·플러그인 0.13.373·imagespec 1.0.1입니다. 정확한 명령은 다음과 같습니다.

```bash
cd /home/eigger/hass-standards-review-t3-final-1MjOtG
.venv/bin/python -m unittest discover -s tests -v > tools-tests.log 2>&1
.venv/bin/python scripts/check_repository.py
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
/home/eigger/hass-standards-review-ha-s3tDc4/.ha-venv/bin/python -m unittest discover -s tests -p test_payload_runtime.py -v > ha-tests.log 2>&1
```

도구 환경의 discovery에서는 146개 중 도구 140개가 성공하고 중앙 HA 6개가 skip되었습니다. 별도 HA 환경에서 그 6개를 전부 실행했으므로 서로 다른 146개 실행 성공으로 기록합니다.

번역 검증의 점이 포함된 키와 중첩 키 충돌은 tuple 경로와 object 노드 비교로 수정하고 회귀 사례를 추가했습니다. 작성 기반은 Python 3.9 문법으로 파싱하지만 생성된 통합의 실제 최소/current HA 성공 결과는 없습니다. 실제 entry·외부 client·설정 필드·액션 계약·기기 설명은 미작성이며 생성 파일의 TODO/예외와 pending을 유지합니다.

독립 실제 HA negative smoke에서 플러그인의 regular `custom_components` 패키지가 생성물을 가려 IntegrationNotFound가 발생했습니다. 빈 패키지 marker와 개별 테스트의 실제 domain const import를 추가했습니다. marker만 추가한 초기 보완은 충분하지 않았으며, 최종 보완 후 생성물을 수정하지 않은 실제 loader 재검증에서 의도한 미구현 예외에 도달했습니다. 이 변경은 HA loader를 mock하거나 fixture를 우회해 통과시키는 처리가 아닙니다.

독립 리뷰는 2026-10-19에 [공식 파일 구조](https://contributors.home-assistant.io/core/integrations/file-structure/)·[config entry 생명주기](https://contributors.home-assistant.io/core/integrations/config-entries/)·[커스텀 통합 번역](https://contributors.home-assistant.io/core/integrations/translations/#custom-integrations) 원문을 재확인했습니다. 기본/선택 모듈 역할, setup 준비 후 플랫폼 전달·unload 후 정리 배치, 완성된 en.json 직접 배포와 미해결 Core 참조 거부는 구조상 부합합니다. 이는 생성물의 실제 최소/current HA 로딩 검증이 아니며 중앙 HA 회귀 6건도 생성된 통합의 동작을 검증한 결과가 아닙니다. 공식 근거 목록은 [sources](sources.md)를 유지합니다.

## T4 변경분 검증

| 담당·범위 | 명령·검사 | 현재 결과 |
|---|---|---|
| 중앙 검사 구현 담당, Windows Python 3.14.6 | `python -m unittest discover -s tests -p test_repository_contract.py -v` | 신규 11개 성공; 미사용 payload 분기의 잘못된 keyword 타입·스킬 상대 링크 회귀 포함 |
| 중앙 검사 구현 담당, 같은 변경분 | 해당 코드 Ruff check/format | 성공·2개 파일 |
| 중앙 검사 구현 담당, 같은 변경분 | `PYTHONUTF8=1`에서 `python scripts/check_repository.py` | 기존 양언어 README 개행의 header 보호 오류로 미통과; Linux 전체 검사 대기 |
| 통합 검사 구현 담당 | `standards/validation.py` 연결과 신규 생성물 회귀 초기 12개·추가 후 15개 | 최종 native 환경 15개 성공 보고 수신; 아래 전체 독립 실행 결과와 구분 |
| 최종 독립 검증, Linux | 전체 도구 회귀·별도 실제 중앙 HA 회귀 | 도구 166개와 중앙 HA 6개, 서로 다른 172개 모두 실행 성공; 중앙 HA 6개 12.493초 |
| 최종 독립 검증, 같은 snapshot | 저장소 검사·Ruff check/format | 문서 37개·workflow 7개 검사 성공·Ruff 성공·80개 파일 |
| 최종 독립 검증, 실제 CLI | 생성 초안·정상 고유 static control·명백한 skip 사례 | 초안 sentinel 종료 1·정상 control 종료 0·모두 대상 불변; module pytest skip와 명백한 unittest skip는 TEST-07 종료 1 |
| 최종 독립 검증, 문서 7개 반영 | 저장소·diff 검사 | 문서 37개/workflow 7개 검사 성공·diff 검사 종료 코드 0·코드 7개 fingerprint 불변·문서 필수 지적 없음 |

최종 snapshot은 `/home/eigger/hass-standards-review-t4-GodQr4`, 실제 CLI 산출물은 `/home/eigger/hass-t4-final-cli-smoke-324tl_hd`이며 초안 로그는 그 아래 `generated-draft-check.log`입니다. 코드 7개 fingerprint는 공유 작업 트리와 같고 manifest SHA-256은 `6bb396572d1ff5a8a580bc144543278726817342666aed93e396b28a6ed511e5`입니다. 이 값은 Git 커밋 SHA가 아닙니다. 필수 미해결 지적은 없으며 수정 전 170/171개 결과를 최종 근거에 재사용하지 않았습니다.

환경은 T1~T3와 같습니다. 정확한 명령은 다음과 같습니다.

```bash
cd /home/eigger/hass-standards-review-t4-GodQr4
.venv/bin/python -m unittest discover -s tests -v > tools-tests-final.log 2>&1
.venv/bin/python scripts/check_repository.py
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
/home/eigger/hass-standards-review-ha-s3tDc4/.ha-venv/bin/python -m unittest discover -s tests -p test_payload_runtime.py -v > ha-tests-final.log 2>&1
```

도구 discovery의 172개 중 도구 166개가 성공하고 중앙 HA 6개는 skip되었으며 별도 환경에서 해당 6개를 모두 실행했습니다. 정상 static control의 종료 0은 실제 HA 기능 성공이 아닙니다. 동적으로 계산한 skip·helper 제어 흐름을 일반적으로 증명하는 정적 분석은 제공하지 않으며 실제 실행과 독립 리뷰를 유지합니다.

중앙 검사는 공유 `contract`의 스키마 vocabulary·타입 판정과 `scaffold` 렌더러를 재사용합니다. 추가하는 것은 스키마 정의 자체의 keyword 타입·로컬 참조·자산 등록·AST/JSON/YAML·실제 구현 단계 리소스 무결성입니다. 중앙 작성 기반의 의도적인 TODO는 허용하되 실제 적용 통합의 미작성 검사를 면제하지 않습니다. 후속 스킬 디렉터리가 없다는 이유로 구현 완료를 주장하지 않으며 실제 디렉터리가 생기면 SKILL 진입 파일과 공유 문서 검사기를 통한 모든 스킬 Markdown의 상대 링크를 검사합니다.

생성물 검사는 기존 `check_integration.py <target> --check`와 승인 예외 경로로 연결했습니다. 정적 구조·번역 키/placeholder·대응 테스트의 알려진 활성 assertion·SHA·정확한 중앙 작성 기반 미완성 표시를 확인합니다. 실제 HA 기능 실행·동적 코드의 모든 의미·번역 의미 검증은 별도입니다. workflow/action 파일 자체와 caller checkout·action_path는 변경하지 않았습니다.

## 남은 검증과 한계

T4 구현·독립 코드/문서 검증과 문서 반영 후 저장소 재검사는 완료했고 최종 커밋·원격 CI 결과가 필요하며 T5 실제 스킬 분기는 미구현입니다. 생성 초안의 실제 HA negative smoke는 수행했지만 실제 신규·기존 통합의 HA minimum/current 성공, HACS/Hassfest, UI 번역·기기 의미·하드웨어 검증은 수행하지 않았습니다. 중앙 fixture와 중앙 도구의 회귀 성공을 외부 통합 도입 완료로 기록하지 않습니다.
