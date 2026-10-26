# 중앙 표준 자동 업데이트

**CI-13 필수**: 채택 리포의 중앙 참조는 native Dependabot의 `github-actions` daily 검사와 첫 번째 `central-standards` group으로 한 PR에서 갱신합니다. 그룹 패턴은 `eigger/hass-repo-standards`와 `eigger/hass-repo-standards/*`를 함께 사용합니다. Dependabot은 tagged composite action을 리포 이름, reusable workflow를 전체 경로로 식별하므로 두 이름 모두 포함해야 합니다. patch·minor는 필수 CI 통과 후 squash 자동 머지, major는 수동 검토합니다. 통합 버전·태그·릴리스를 만들지 않습니다.

각 리포의 [update_standards.yml](../templates/integration/.github/workflows/update_standards.yml)은 exact immutable 중앙 release의 [standards-update.yml](../.github/workflows/standards-update.yml)을 호출합니다. 추가 PAT·GitHub App 비밀키 없이 리포의 `GITHUB_TOKEN`을 사용합니다. workflow 파일을 바꾸는 주체는 GitHub 기본 Dependabot입니다. `actions: write`는 검증 dispatch 권한이며 workflow 파일 수정 권한을 제공하지 않습니다.

중앙 updater는 신뢰하는 기본 브랜치와 거기 기록된 중앙 full SHA만 checkout합니다. PR은 Git API로 데이터만 읽고 실행하지 않습니다. 같은 리포의 Dependabot PR인지, 기본 브랜치 대상인지, 기존 workflow의 중앙 `uses` ref만 변경했는지, 예외 외 모든 중앙 참조가 같은 새 exact stable tag인지 확인합니다. published immutable release와 peeled SHA를 attest한 다음 `.hass-standards.json`과 `STANDARDS.md`의 현재 참조만 하나의 commit으로 맞춥니다. 기록된 예외·이력은 보존하며 부분 그룹·다른 파일 변경·파일 추가/삭제·symlink/mode 변경·downgrade는 실패합니다. PR HEAD가 바뀌면 덮어쓰지 않고 실패합니다.

메타데이터 commit은 PR 이벤트를 다시 발생시킨다고 가정하지 않습니다. 모든 `pull_request` validator의 `workflow_dispatch` 지원을 먼저 확인하고 PR 브랜치로 직접 dispatch합니다. 각 validator가 성공해야 기존 branch protection에 따라 자동 머지됩니다. dispatch 오류도 실패로 전파합니다. 관리자 우회나 required check 완화는 사용하지 않습니다. 같은 major에서만 updater가 자동 squash를 예약합니다.

## 첫 설치와 호환성

기존 리포의 최초 설치는 workflow 수정 권한을 가진 운영자가 검토 가능한 PR로 수행합니다. 중앙 release를 publish하고 원격 검증한 후 다음 명령으로 변경 계획을 출력합니다. `--write`를 추가하면 관리 파일만 수정합니다.

```text
python scripts/install_standards_updater.py /absolute/consumer --release v1.1.0
python scripts/install_standards_updater.py /absolute/consumer --release v1.1.0 --write
```

설치기는 중앙 `uses` 참조, 단일 descriptor·문서 기록, daily Dependabot group, updater caller를 함께 변경합니다. `standards_update`는 `{"provider":"dependabot","workflow":"update_standards.yml"}`로 명시합니다. 이 opt-in의 release consumer는 `python-tests.yml`·`dependency-update.yml`의 `standards-ref` 입력을 생략하고, 실행 시 체크아웃된 `.hass-standards.json`의 검토 full SHA를 사용합니다. 일반 검증 중 네트워크로 최신 tag를 해석하지 않습니다. 기존 opt-in 없는 caller는 명시적 `standards-ref` 동작을 유지합니다. 새 중앙 버전을 설치할 때 추가로 바뀐 규칙이 있으면 정상 CI가 이를 검출하며 우회하지 않습니다.

예약 reconciliation은 이벤트 실패를 재시도합니다. 수동 실행의 PR 번호가 0이면 열린 Dependabot 표준 PR 전체를 검사합니다. 운영자가 명시적으로 번호를 입력한 `workflow_dispatch`만 사람이 만든 중앙 참조 전용 PR도 허용하며, 이 경우 metadata 보정·검증만 수행하고 자동 머지를 예약하지 않습니다. 자동 머지는 작성자가 Dependabot인 same-major PR에만 적용합니다. PR 코드를 실행하지 않는 검증 경계는 같습니다.

## 누락 감사

GitHub의 [기본 cooldown](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference)은 새 버전 제안을 3일 지연할 수 있습니다. 설치기는 중앙 dependency의 두 이름만 `cooldown.exclude`에 명시해 다음 daily 검사 대상으로 만들고, 나머지 패키지의 대기 정책은 보존합니다. 이 보정은 v1.1.1부터 포함됩니다. 검사기는 명시적 cooldown에서 이 exclude가 빠지면 CI-13으로 실패합니다. cooldown 설정 자체가 없었던 v1.1.0 설치의 호환성은 유지하며 다음 bootstrap 때 보정합니다.

[standards-consumers.json](../standards-consumers.json)은 운영 대상 목록입니다. [audit-consumers.yml](../.github/workflows/audit-consumers.yml)은 매일 계정의 모든 nonfork·nonarchived 리포와 실제 기본 브랜치 tree를 페이지 끝까지 열거합니다. GitHub code search의 인덱싱·결과 제한에 의존하지 않습니다. 발견된 중앙 참조/descriptor와 등록 목록을 대조하므로 새 리포 등록 누락도 실패합니다. 읽기 실패·잘린 tree·버전/메타데이터 불일치·설치 누락·최신 release 업데이트 PR 부재를 성공으로 처리하지 않습니다. 최신 버전이면 `current`, 업데이트 PR이 있으면 `pending`과 링크를 기록합니다. pending은 CI 통과나 머지 완료를 뜻하지 않습니다. 감사는 읽기 전용이며 다른 리포를 수정하지 않습니다.

Dependabot 검사 시각과 Actions schedule에는 지연이 있을 수 있습니다. 새 release 직후 아직 PR이 없다면 감사가 실패하고 다음 daily 실행에서 재평가합니다. 운영자는 해당 리포의 Dependabot update job과 updater run을 확인합니다. 기존 필수 CI, major 수동 검토, 브랜치 자동 삭제 설정은 별개로 유지합니다.

공식 근거: [Dependabot GitHub Actions 지원](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot), [group·allow·ignore 설정](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file), [GITHUB_TOKEN 이벤트 제한](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication), [workflow 수정 권한 경계](https://github.github.com/gh-aw/reference/glossary/#allow-workflows-allow-workflows).
