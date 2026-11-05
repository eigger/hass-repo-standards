# README 통일 작업 계획

2026-11-05 사용자 요청에 따른 부분 문서 변경입니다. 각 리포의 원격 기본 브랜치 최신 커밋과 작업 트리·기존 표준 기준을 확인하고, 영문·한국어 README의 기존 정보를 보존하며 공통 구조와 표현으로 정리합니다. 변경 전후 앵커·링크와 양언어 의미를 비교합니다. 설치 안내는 2026.11 이상 마켓플레이스와 기존 지원 버전 HACS를 구분합니다. 중앙 규칙 변경은 아직 미출시이며 각 통합의 기존 릴리스 pin을 변경하지 않습니다.

## hass-atflee

- 기준: 원격 `master` `f9e46ae71ced3d8a79081fd465befa2de623794d`, 로컬 동일·작업 트리 깨끗함; 채택 `v1.1.5` / `f56987f7f765a774c926fb8005fe5df68bb32451`.
- 계획: 양언어 소개의 HACS 표현을 커스텀 통합으로 바꾸고 metadata도 같이 변경합니다. 2026.11 이상 마켓플레이스 사용자 지정 저장소와 이전 HACS, 기존 수동 설치·재시작·발견·사용자 설정을 설명합니다. 요구사항·제목 표현을 맞추고 모든 기기별 제한과 상세 링크를 보존합니다. 관리 설치 배지와 기존 지원 최소를 유지합니다.
- 검증: README 관리 블록·양언어 내용·상대 링크와 기존 기준 검사기를 확인합니다. 원격 CI·실제 UI·기기 실행은 수행하지 않으며 완료로 표시하지 않습니다.

- 로컬 적용: 양언어 README와 설정 metadata 변경. 2026-11-05 Windows Python으로 LF 정규화한 임시 snapshot에서 중앙 `check_integration.py` 종료 0. 원격 CI·UI·실물은 미실행. 중앙 snapshot `check_repository.py`는 39문서·16 workflow 검사 종료 0; 원래 Windows checkout에서는 CRLF 헤더 오류로 실패했습니다.

## hass-ble-esl

- 기준: 원격 `main` `6773eb325dfb72a2c5516c86c8b47a8980db5537`, 별도 detached 작업 트리; 기존 `v1.1.5` / `f56987f7f765a774c926fb8005fe5df68bb32451`. 지원 최소 2025.12.0, 기존 Default 등재 근거 2026-10-21.
- 계획: 표시 제목·양언어 소개와 metadata를 맞추고 설치 안내를 2026.11 이상 마켓플레이스와 이전 HACS로 구분합니다. 사진·태그별 검증 상태·Bluetooth·이전·경고·예제와 상세 문서를 보존합니다. 제목과 본문의 앵커는 가능한 한 유지합니다.

- 2026-11-05 HACS 공식 default 목록에 등재 확인. 양언어 README 및 metadata 변경 후 중앙 검사기 종료 0; UI·원격 CI 미실행.

## hass-ble-led-sign

- 기준: 원격 `master` `c4c932c961bf9b0cb8c1d36f2a2c29620fcdc714`, 로컬 동일·깨끗함; 기존 기준 `v1.1.5` / `f56987f7f765a774c926fb8005fe5df68bb32451`, 최소 2025.1.0.
- 계획: 제목·소개 metadata와 설치를 통일하고 이전 HACS·수동 설치·제거를 보존합니다. 중복 지원·라이선스 절의 실질 내용은 기존 관리 영역으로 합치며 payload 문서 링크는 문서 절로 옮깁니다. 기기 표·설정·예제·제한을 보존합니다.

- 로컬 적용 후 중앙 검사기는 원본 Windows checkout에서 TEST-03 CRLF 차이로 실패했습니다. LF 정규화 임시 snapshot에서 동일 검사 종료 0. UI·원격 CI 미실행.

Atflee 중앙 규칙 및 적용 diff 독립 리뷰: 2026-11-05 Codex `readme_review`, 지적 없음. 리뷰는 UI 실행이나 테스트를 포함하지 않습니다. 위 세 리포 외에는 아직 변경·검증하지 않았습니다.

## 중앙 검토와 검증

- 기준 `114fbdbe95d1fefe233a6babc18c1ddc0b551983`, 미커밋 작업 트리. 독립 리뷰 `central_review`에서 템플릿 제목 불일치와 YAML 전용 통합의 설정 분기 누락을 수정하고 재검토 결과 추가 지적 없음.
- 2026-11-05 LF 정규화 임시 snapshot의 WSL Ubuntu Python 3.14.4, PyYAML 6.0.3, packaging 26.0에서 `python3 -m unittest discover -s tests` 268개 통과, `python3 scripts/check_repository.py` 40문서·16 workflow 통과. Windows 원본 테스트는 CRLF 판정 8건과 symlink 권한 3건으로 실패했습니다. 원격 CI는 미실행이며 이번 증거로 표시하지 않습니다.
- 중앙 변경은 미출시이며 대상 리포의 기존 release pin은 변경하지 않습니다. 본문 수동 정리는 사용자 요청 범위이며 자동 렌더러는 관리 영역만 갱신합니다.

### Atflee 최종 검토

기기 목록과 기능 항목을 양언어에서 분리했습니다. 독립 리뷰 `central_review`는 실제 config flow·기기 발견과 사용자 지정 저장소, 기존 안내·번역·링크 보존을 확인하고 필수 수정 지적이 없었습니다. 기능 분리 후에도 같은 문장을 유지함을 재검토했습니다. 2026-11-05 LF 정규화 snapshot에서 중앙 `check_integration.py` 종료 0; 마지막 변경은 제목 앞 빈 줄만 추가했습니다. HA UI·실물·원격 CI는 미실행이며 README 부분 변경은 전체 재채택이 아닙니다.
