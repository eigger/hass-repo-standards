# 중앙 updater 검증 기록

2026-10-26 구현 후보 `dc38155`를 기준으로 실행 경계와 설치 계획을 검증했습니다. GOV-05에 따라 구현자가 아닌 독립 리뷰 담당자가 코드를 읽고 Dependabot dependency 이름 누락·legacy import 회귀·rebase 중단·ignore 정책·실패 PR 감사 누락을 지적했으며 반영했습니다. 실제 배포·머지와 아래 로컬 증거는 구분합니다.

- 중앙 regression: 252 tests 성공, 실제 HA 전용 6개 skip. Python 3.14.5, PyYAML 6.0.3, packaging 26.3, Ruff 0.17.1. canonical `TMPDIR=/private/tmp` 사용. payload 실제 HA 6개 검사는 전용 원격 job에서 실행하며 로컬 도구 venv에는 설치하지 않았습니다.
- Ruff check/format, `check_repository.py`, actionlint 1.7.12를 실행했습니다.
- 등록된 22개 리포의 실제 기본 브랜치를 새 clone으로 읽어 bootstrap 계획을 생성했습니다. 복사본에 후보 descriptor를 적용한 전체 `check_integration.py` 정적 검사에서 22/22 오류 없음. hass-catprinter의 기존 승인된 categories 예외는 그대로 보고·보존했습니다. 이 결과는 원격 CI 성공을 의미하지 않습니다.
- [GITHUB_TOKEN 권한 실험](https://github.com/eigger/hass-repo-standards/actions/runs/40333523040): 격리된 운영자 생성 브랜치에서 workflow를 변경한 HEAD를 부모로 두고, `contents: write` 기본 토큰이 비workflow JSON blob만 추가하는 Git tree·commit·기존 ref 갱신을 실제 성공했습니다. 생성 commit은 `efb4e25c3a685771fad28e3b34c54e409a92ef02`입니다. runtime writer가 workflow blob을 쓰지 않는 설계의 권한 경계를 확인했습니다. 실험 브랜치는 결과 확인 후 삭제하며 기본 브랜치에는 실험 코드를 반영하지 않습니다.

생성 metadata commit에는 `[dependabot skip]`을 기록해 native Dependabot이 후속 rebase를 계속할 수 있게 합니다. `rebase-strategy: disabled`는 거부합니다. 근거는 [extra commits 위 rebase 허용](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-dependabot-prs)입니다. 이후 synchronize/예약 reconciliation이 metadata를 다시 맞추며, 기본 브랜치와 다른 코드 변경은 쓰기 전에 거부합니다.

## 실제 소비 리포 파일럿

- [hass-opinet PR24](https://github.com/eigger/hass-opinet/pull/24)는 v1.1.0 bootstrap과 중앙 cooldown 제외를 적용했습니다. Standards·현재/최소 HA·lint·HACS·Hassfest·Dependabot config 검사 모두 성공 후 squash `80a6d8c7f5cda0273b3909cb31f29874dd17bf07`로 반영했습니다.
- native Dependabot이 중앙 dependency 5종을 묶은 [PR25](https://github.com/eigger/hass-opinet/pull/25)를 실제 생성했습니다. [native update job](https://github.com/eigger/hass-opinet/actions/runs/40336529334)에서 cooldown 제외와 v1.1.0→v1.1.1 선택을 확인했습니다.
- [PR target updater 실행](https://github.com/eigger/hass-opinet/actions/runs/40336671106)이 기본 GITHUB_TOKEN으로 metadata commit `43670519940f31416e821c47896ef2c914e600ee`를 생성하고 세 validator를 명시적으로 dispatch했습니다. 이 commit은 JSON·STANDARDS 두 파일만 변경했습니다.
- 최초 [manual run](https://github.com/eigger/hass-opinet/actions/runs/40336503168)은 GitHub가 수동 입력 0을 문자열로 전달해 reusable number 입력 검증에서 실패했습니다. 정적/actionlint로는 이 서버 경계를 확인하지 못했습니다. caller를 format/fromJSON으로 보정한 격리 브랜치의 [실제 manual 0 재실행](https://github.com/eigger/hass-opinet/actions/runs/40337202450)은 성공했고 이미 동기화된 PR25에 추가 metadata commit 없이 validator dispatch·자동 squash 예약을 재시도했습니다.
- 새 caller 입력식은 v1.1.2부터 설치합니다. tag-only 업그레이드 호환성을 위해 checker는 이전 식 하나도 명시적으로 정규화해 허용하고, author guard·permissions·다른 caller 필드 변경은 계속 거부합니다. 이 호환성에 회귀 검사를 추가했으며 updater 단위 검사 11개를 통과했습니다.

전체 22개 배포·최종 기본 브랜치 감사 결과는 별도 현황에 기록합니다. 위 파일럿 성공만으로 전체 배포 완료를 의미하지 않습니다.
