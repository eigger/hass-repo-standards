# 릴리스와 유지보수

**REL-01 필수**: 통합은 SemVer를 기본으로 합니다. breaking API·entity ID·설정·프로토콜 변경은 major, 호환 기능은 minor, 수정은 patch입니다. HA 최소 버전 상승과 의존 라이브러리 하한 상승은 사용자 영향과 근거를 release notes에 기록합니다. 적용 버전은 통합의 기존 버전 정책과 함께 검토합니다.

**REL-02 필수**: release checklist는 lint/test, HACS/Hassfest, 지원 버전 확인, tag/manifest 일치, 변경 기록, 마이그레이션/제한 안내입니다. `GITHUB_TOKEN` bot PR의 후속 required checks를 별도로 확인합니다. 테스트 통과만으로 실제 장치 검증을 주장하지 않습니다.

**REL-03 필수**: 릴리스 노트에는 사용자에게 바뀐 동작, 필요한 조치, 추가/종료된 지원, 알려진 제한을 씁니다. bot의 manifest 수정만으로 integration version과 tag를 자동 올리지 않습니다. 릴리스는 검토 후 별도 작업입니다.

**REL-04 필수**: 통합 이전·통합·중단은 README 상단에 새 경로, 유지보수 상태, domain/장치 재등록 여부를 적습니다. 기존 설치가 자동으로 이전된다고 가정하지 않습니다. 이전된 리포는 일반 feature 작업 대상으로 자동 편입하지 않습니다.

**REL-05 권장**: dependency/HA API 갱신은 기능 변경과 분리하고 CI 결과를 확인합니다. 규칙 리포의 업데이트는 해당 리포의 채택 PR을 통해 반영합니다.

## 중앙 표준 릴리스 (REL-06)

**REL-06 필수**: 이 중앙 리포의 배포 단위는 규칙·템플릿·schema·scripts·actions·reusable workflows·skills입니다. stable version은 SemVer exact `vX.Y.Z` immutable GitHub Release이며 수정은 새 version으로 발행합니다. published release tag의 이동·재사용·asset 교체, `v1`/`v1.2`·branch·`latest` 참조는 금지합니다. 현황표·통계만의 운영 갱신은 릴리스를 강제하지 않습니다.

release 전에는 candidate commit에서 `check_repository`, regression tests, actionlint와 workflow fixture를 통과시킵니다. workflow는 release metadata asset을 포함한 draft까지만 만들며 published release를 만들지 않습니다. immutable-release 설정 조회에는 Administration 권한이 필요하므로 `GITHUB_TOKEN`으로 그 경계를 우회하지 않습니다. 관리자 권한의 운영자는 draft의 asset/tag/SHA와 immutable setting을 `scripts/central_release_operator.py`로 fail-closed 확인한 뒤 publish하고, 즉시 `verify-release`로 원격 immutable/peeled tag를 attest합니다. 실패한 draft는 published 성공이 아니며 수정·재검증 후 새 version 또는 명시적 정리 절차를 사용합니다. release metadata의 candidate/squash commit SHA는 runtime asset에만 만들고 tracked 파일에 self SHA를 쓰지 않습니다.

release notes에는 exact version과 resolved SHA, contract version, internal action dependency SHAs, 영향·이관 방법, 검증 명령·CI URL, 알려진 제한을 기록합니다. 발행 뒤 `verify-release`로 immutable 상태와 peeled commit을 확인하고 그 결과를 adoption evidence에 연결합니다. 첫 목표 `v1.0.0`은 이 절차가 완료될 때까지 발행된 것으로 간주하지 않습니다.

관리자 운영 예시는 준비 workflow가 만든 draft의 candidate SHA가 `<sha>`일 때 다음 순서입니다. `central_release_operator.py` 실패는 publish 중단이며, 설정 조회 실패·기존/다른 draft·asset 누락·tag 불일치를 성공으로 취급하지 않습니다.

```text
python3 scripts/central_release_operator.py --repository eigger/hass-repo-standards --version v1.0.0 --candidate-sha <sha>
gh release edit v1.0.0 --repo eigger/hass-repo-standards --draft=false
python3 scripts/manage_integration.py verify-release --repository eigger/hass-repo-standards --tag v1.0.0 --resolved-sha <sha> --output <outside-worktree>/release-verification.json
```

## ZIP 릴리스 첨부

중앙 `actions/release-zip`과 [caller 템플릿](../templates/integration/.github/workflows/release.yml)은 검토한 legacy SHA 또는 REL-06 exact immutable central release tag로 고정합니다. 이는 중앙 자체 REL-06 릴리스와 통합 ZIP 배포를 구분하는 설명이며, caller는 대상 통합의 `release: published` 이벤트에서 해당 태그 커밋을 checkout하고 ZIP을 기존 릴리스에 첨부할 뿐 통합의 릴리스·태그를 생성하거나 manifest 버전을 덮어쓰지 않습니다. 태그의 `v` 하나를 제외한 값과 manifest.version이 다르면 실패합니다. 실제 release tag commit과 checkout HEAD도 일치해야 합니다.

packager는 Git으로 추적된 통합 파일만 포함하고 캐시·심볼릭 링크를 배제/거부합니다. README·tests·저장소 metadata와 추적되지 않은 파일을 넣지 않습니다. 기존 asset을 덮어쓰지 않으며 동일 asset 이름으로 재실행하면 업로드가 실패합니다. 기존 다운로드 수를 지우는 `--clobber`로 우회하지 않습니다.

배포 전에 같은 커밋의 Tests·Validate 성공을 확인해야 합니다(CI-11). ZIP job의 성공은 태그/manifest·패키지 구조 검증이며 실제 HA 회귀·기기 검증을 대체하지 않습니다. Published 이벤트부터 ZIP 업로드까지 잠시 asset이 없을 수 있고 job 실패 시 릴리스 제공이 불완전합니다. 실패를 공개 배포 성공으로 취급하지 말고 원인을 수정해 같은 태그의 올바른 ZIP을 첨부합니다. 기존 파일이 있다면 확인 없이 교체하지 않습니다. Immutable releases가 활성화되어 published 이후 첨부할 수 없는 리포에는 이 caller를 적용하지 않고 draft 단계 패키징으로 별도 설계합니다.

기존 릴리스는 해당 태그의 기존 hacs.json으로 설치하므로 소급 수정하지 않습니다. 다음 릴리스부터 ZIP 방식으로 전환하며, 버전 변경이나 새 릴리스 발행은 별도 사용자 요청 범위입니다. HACS의 표시값은 선택한 asset의 다운로드 수를 읽으며 ZIP 설치 설정 없이 첨부 파일만 있어도 표시될 수 있습니다. 실제 HACS 설치가 asset 다운로드 수에 반영되게 하려면 ZIP 설치 설정과 실제 첨부 파일을 함께 제공합니다.
