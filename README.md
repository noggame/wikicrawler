# 소개

wikipedia (한국) 웹사이트에서 필요한 데이터를 정제해 사용하기위한 프로그램

# 사용법

### 실행환경 및 설치

:white_check_mark: Python v3.9.7 

:white_check_mark: Python packages = [requests, beautiful soup 4]

> $ pip install requests bs4

### 실행

[main.ipynb](./main.ipynb) 파일 참고

# :wrench:​ 환경설정

[config.ini](./config.ini) 파일 설정

- identifier : 출력 시 접두어/접미어
- filter : 데이터 처리 확인/제외 정보 정의
    - available_tag    : <div class="mw-parser-output">의 자식 태그 중 `분석` 대상 명시
    - exclude_tag      : <div class="mw-parser-output">의 자식 태그 중 `제외` 대상 명시
    - exclude_class    : 분석 중 해당 class 명을 가지는 태그는 무시
    - exclude_passage  : 불필요한 Passage 목록 제거 (Passage의 Title 기입)
    
<br>

# :bookmark: Updates & History

[history.md](./history.md) 파일 참조

<br>

# Ref.
크롤러 만들기 [참고](https://www.geeksforgeeks.org/web-scraping-from-wikipedia-using-python-a-complete-guide/)