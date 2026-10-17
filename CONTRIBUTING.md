# 기여

규칙은 배경·적용 범위·필수/권장·공식 출처를 함께 작성합니다. 변경한 입력의 호환성을 유지하고 파괴적 변경은 표준 major 정책에 따릅니다. 테스트는 네트워크·GitHub 쓰기 없이 실행할 수 있어야 합니다.

```bash
python3 -m pip install -r requirements_dev.txt
python3 -m ruff check .
python3 -m ruff format --check .
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

원격 integration 검증과 실제 GitHub PR 생성은 unittest에서 실행하지 않습니다. workflow/action을 변경하면 actionlint와 해당 fixture 검증을 수행합니다.
