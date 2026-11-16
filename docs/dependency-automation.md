# Manifest 의존성 자동 병합과 정리

CI-09의 선택 기능입니다. `blesession`·`imagespec`를 사용하는 통합에만 관리자가 한 번 설치합니다. 기존 updater는 PR 생성 전 exact 새 하한·실제 HA·payload·지정 validation-command를 검사하고, 새 controller는 별도의 필수 CI까지 통과한 PR만 squash merge합니다. integration version·tag·release는 자동 생성하지 않습니다.

## 설치와 중앙 버전 갱신

새 immutable 중앙 release를 REL-06으로 발행·attest한 뒤 다음 명령으로 변경 계획을 확인합니다. `--write`는 관리 파일만 적용합니다.

```text
python scripts/install_dependency_automation.py /absolute/consumer --release v1.3.0
python scripts/install_dependency_automation.py /absolute/consumer --release v1.3.0 --write
```

설치기는 기존 중앙 updater 설치기를 재사용해 모든 중앙 참조·descriptor·STANDARDS 기록을 같은 release로 맞추고, 중앙 템플릿의 `merge_dependencies.yml`을 생성합니다. domain·packages는 기존 `update_dependencies.yml`에서 읽습니다. 지원 최소·manifest·통합 본문은 바꾸지 않습니다. 설치 후 중앙 버전 참조는 기존 native Dependabot group과 standards updater가 계속 갱신합니다. 매 중앙 변경마다 로직을 대상에 복사하지 않습니다.

새 caller의 `actions: write`는 validator dispatch에만 사용하고 `contents: write`·`pull-requests: write`는 병합·정리에 사용합니다. 기존 dependency updater의 권한은 늘리지 않습니다. GitHub의 Actions PR 생성 허용 설정은 기존 updater에 필요하지만, 이 controller는 PR 생성이나 자기 승인을 하지 않습니다. 추가 PAT/App secret을 요구하지 않습니다.

## 실행 경계

`Update dependencies` workflow 완료 후 빠르게 실행하며 daily schedule·수동 실행이 누락 복구와 정리를 담당합니다. 공개 저장소의 60일 비활성 schedule 중단은 GitHub 제약입니다. updater와 controller는 같은 concurrency group을 사용해 bot branch 변경·정리를 직렬화합니다.

controller는 신뢰하는 기본 브랜치와 descriptor의 resolved full SHA 중앙 tools만 checkout합니다. PR 코드는 실행하거나 import하지 않습니다. 같은 저장소·기본 브랜치 대상·`github-actions[bot]` 작성·`bot/manifest-dependencies` branch의 열린 PR만 허용합니다. 현재 기본 브랜치 위 한 commit이어야 하며, 고정 Git tree 전체를 비교해 해당 domain의 기존 일반 파일 manifest 외 변경을 거부합니다. requirement의 순서·패키지·extras·operator·marker·나머지 manifest 값은 보존하고 선택된 패키지의 stable same-major 버전 증가만 허용합니다. major·downgrade·임의 파일·symlink·부분 tree 조회는 실패합니다.

검사한 head에 고유한 임시 validation branch를 만들고 거기서 모든 `pull_request` validator를 명시 dispatch합니다. 각 validator는 workflow_dispatch를 지원해야 하며 Standards·Tests·Validate가 모두 필요합니다. 이전 성공을 재사용하지 않고 새 run ID·head SHA·validation ref·event가 일치하는 실행의 실제 success를 기다립니다. dispatch 실패·timeout·실패·skip은 병합하지 않고 PR을 남깁니다. head 검증이 성공해도 GitHub가 PR의 test merge commit에 연결한 필수 검사는 아직 진행 중일 수 있으므로, GraphQL mergeStateStatus가 CLEAN이 될 때까지 같은 제한 시간 안에서 기다립니다. 권한 오류는 상세 응답을 남기고 즉시 실패하며 HTTP405/409 경합만 준비 상태를 재검사합니다. 대기 후 PR head와 관측한 기본 브랜치가 바뀌면 중단합니다.

GitHub REST merge는 expected head SHA만 원자적으로 고정하며 expected base SHA 입력은 없습니다. 마지막 재검사와 merge 사이의 기본 브랜치 push까지 엄격히 차단하려면 저장소의 strict up-to-date required checks/merge queue 정책이 필요합니다. controller는 이 설정을 임의 변경하거나 관리자 우회를 사용하지 않으며 기존 GitHub 병합 요건을 그대로 따릅니다. 테스트 성공은 검증한 PR head에 대한 증거이고 미래 base 변경이나 실물 동작의 보장이 아닙니다.

임시 validation ref와 병합된 bot branch는 관측 SHA를 지정한 `git push --force-with-lease ... :ref`로 정리합니다. 병합된 같은 저장소 bot PR head와 tip이 같고 열린 PR이 없을 때만 bot branch를 삭제합니다. 다른 작업이 tip을 이동하면 삭제가 실패하며 새 작업을 지우지 않습니다. 임시 ref는 검증 실패 때도 정리하며, 강제 취소로 남은 임시 ref는 운영자가 확인할 수 있습니다. 재사용 bot branch의 과거 병합 잔여물은 daily 정리가 처리합니다.

공식 근거: [workflow dispatch](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event), [workflow run 조회](https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-workflow), [expected SHA squash merge](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request), [git force-with-lease](https://git-scm.com/docs/git-push#Documentation/git-push.txt---force-with-leaseltrefnamegtltexpectgt).
