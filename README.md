# 소개

wikipedia (한국) 웹사이트에서 필요한 데이터를 정제해 사용하기위한 프로그램

# 사용법

### 실행환경 및 설치

:white_check_mark: Python 3.9.7 [requests, beautiful soup 4]
:white_check_mark: 

패키지 설치
```
# Python 3.9.7
pip install requests bs4
```

### 실행

main.ipynb 파일 참고

# :wrench:​ 환경설정

config.ini 파일 수정
- identifier : 출력 시 접두어/접미어
- filter : 데이터 처리 확인/제외 정보 정의
    - available_tag    : <div class="mw-parser-output">의 자식 태그 중 `분석` 대상 명시
    - exclude_tag      : <div class="mw-parser-output">의 자식 태그 중 `제외` 대상 명시
    - exclude_class    : 분석 중 해당 class 명을 가지는 태그는 무시
    - exclude_passage  : 불필요한 Passage 목록 제거 (Passage의 Title 기입)


# :bookmark: Updates & History

[Update 예정]
- 관련 데이터 링크정보 저장/관리 (연관검색 키워드로 사용 예정)
- 사용가능한 태그에 대해 text 정보를 뽑을 때 특정 함수만 호출하도록 수정 (recursion 발생하나 구조단순화 및 재사용성 향상)

[09/13]
- Table, List, Description 적용 (Table의 경우 보완 필요)
- 각주, 외부 링크 등 불필요한 Passage 필터링 적용

[08/21]
- 제목의 "[편집]" 텍스트 제거
- 리스트 태그 붙이기


# :warning: Issue

시험버전으로, 다양한 데이터 포맷에 대한 시험 및 포맷/구조 수정 필요

주요 이슈사항
- 관련 검색어 없을 시 오류/예외 발생
- 셀이 합병된 테이블 처리 필요


# Ref.
크롤러 만들기 [참고](https://www.geeksforgeeks.org/web-scraping-from-wikipedia-using-python-a-complete-guide/)