# 릴리스와 유지보수

**REL-01 필수**: 통합은 SemVer를 기본으로 합니다. breaking API·entity ID·설정·프로토콜 변경은 major, 호환 기능은 minor, 수정은 patch입니다. HA 최소 버전 상승과 의존 라이브러리 하한 상승은 사용자 영향과 근거를 release notes에 기록합니다. 적용 버전은 통합의 기존 버전 정책과 함께 검토합니다.

**REL-02 필수**: release checklist는 lint/test, HACS/Hassfest, 지원 버전 확인, tag/manifest 일치, 변경 기록, 마이그레이션/제한 안내입니다. `GITHUB_TOKEN` bot PR의 후속 required checks를 별도로 확인합니다. 테스트 통과만으로 실제 장치 검증을 주장하지 않습니다.

**REL-03 필수**: 릴리스 노트에는 사용자에게 바뀐 동작, 필요한 조치, 추가/종료된 지원, 알려진 제한을 씁니다. bot의 manifest 수정만으로 integration version과 tag를 자동 올리지 않습니다. 릴리스는 검토 후 별도 작업입니다.

**REL-04 필수**: 통합 이전·통합·중단은 README 상단에 새 경로, 유지보수 상태, domain/장치 재등록 여부를 적습니다. 기존 설치가 자동으로 이전된다고 가정하지 않습니다. 이전된 리포는 일반 feature 작업 대상으로 자동 편입하지 않습니다.

**REL-05 권장**: dependency/HA API 갱신은 기능 변경과 분리하고 CI 결과를 확인합니다. 규칙 리포의 업데이트는 해당 리포의 채택 PR을 통해 반영합니다.
