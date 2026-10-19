# 템플릿·스킬 구현 검증 기록

2026-10-19. [작업지시서](template-skill-tasks.md)의 중앙 도구 구현 결과를 기록합니다. 개별 통합의 채택 결과나 지원 최소/current HA 검증을 대신하지 않습니다.

## 검증 대상과 단계

설계 baseline은 `77c279406d7b10e13cc72fa25495a6b648b9d98f`입니다. T1은 `1968bbf446e665ab6b496bc62227bf1620d6fd1c`로 커밋하고 [PR #2](https://github.com/eigger/hass-repo-standards/pull/2)에 제출했으며, 해당 커밋의 [원격 CI](https://github.com/eigger/hass-repo-standards/actions/runs/39194455236) 네 검사가 모두 성공했습니다. 설계 [PR #1](https://github.com/eigger/hass-repo-standards/pull/1)은 merge commit `87ae6450ebc3e2d5ad7a5b835f9716eab94ff1a0`, T1 PR #2는 `0fd0dee351965f46b960903201d046f573465d02`로 main에 반영했습니다. main merge CI는 아직 확인 중입니다. T2 검증 대상은 T1 커밋 위의 작업 트리 변경분입니다. T2 최종 커밋과 원격 CI는 아직 미확정입니다. baseline과 T1 검증을 T2 변경 검증으로 재사용하지 않습니다.

| 단계 | 구현·검증 상태 | 남은 작업 |
|---|---|---|
| T1 | 계약·스키마·공통 모듈 구현, 독립 코드/문서 검증·커밋 CI 네 검사 성공·main 병합 | main merge CI 확인 |
| T2 | 읽기 전용 inspect/plan·조사·변경 계획 구현, 독립 코드/문서 검증 완료 | 최종 커밋/CI 근거 확정 |
| T3 | TODO | 새 컴포넌트·테스트 작성 기반, apply·복구 |
| T4 | TODO | 전체 생성 계약과 검사기·CI 연결 |
| T5 | TODO | 두 스킬·설치 및 실행 안내·동작 검증 |
| T6 | TODO | 중앙 생성·갱신 fixture와 별도 범위의 실제 통합 검증 |

계약의 `available` 21개는 기존 원본이 존재한다는 뜻입니다. `pending` 23개는 아직 작성 기반이 없음을 명시합니다. T1은 이 구분과 허용 소유 방식·조건·규칙·경로 토큰·입력을 검증합니다. T2는 `manage_integration.py inspect/plan`을 제공하며 생성/apply 기능은 미구현입니다. 외부 통합 수정·지원 최소 변경·스킬 설치·workflow 수동 실행은 수행하지 않았습니다.

## 현재 사용할 수 있는 T1 API

저장소 루트에서 실행합니다. 다음 코드는 계약을 읽고 검증할 뿐 대상 파일을 생성하거나 변경하지 않습니다.

```bash
PYTHONPATH=scripts python3 -c "from standards.contract import load_contract; print(len(load_contract()['records']))"
python3 -m unittest discover -s tests -p test_standards_contract.py -v
```

`standards.contract.validate_input(data)`는 출처를 포함한 신규 입력을, `validate_document(data, "inventory")`와 `validate_document(data, "plan")`은 조사·계획 CLI 산출물의 스키마를 검증합니다. T2의 실제 inspect/plan 명령과 sourced 입력 예시는 [사용 안내](template-skill-usage.md)에 있습니다. 실제 생성·갱신은 T3 구현 후 안내합니다.

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

## 남은 검증과 한계

T2 코드의 독립 전체 검사와 문서 반영 후 저장소 재검사는 완료했고, T2 최종 커밋 및 원격 CI 결과가 필요합니다. action/workflow는 T1~T2에서 변경하지 않았습니다. T3의 재적용 무차이·부분 실패 복구와 T5의 실제 스킬 분기는 아직 실행할 구현이 없습니다. 실제 신규·기존 통합의 HA minimum/current 조합, HACS/Hassfest, UI 번역·기기 의미·하드웨어 검증은 수행하지 않았습니다. 중앙 fixture와 중앙 도구의 회귀 성공을 외부 통합 도입 완료로 기록하지 않습니다.
