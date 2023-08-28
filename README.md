# 사용법

### 실행황경 및 설치

```
# Python 3.9.7
pip install requests BeautifulSoup
```

### 실행

main.ipynb 파일 참고하여 실행


### 카테고리 구분자 지정

WikiCrawler 클래스 정의 상단부의 변수 수정

``` Python
# ...
class WikiCrawler:
    title_tag = "="
    list_tag = "-"
# ...
```


# Todo
- 관련 검색어 없을 시 오류/예외 발생
- 테이블 처리 여부 결정 및 수행
- 각주 및 불필요 H태그 확인 및 제거
- 관련 데이터 링크 정보 저장/관리 (연관검색으로 사용)


# 완료
- [08/21] 제목의 "[편집]" 텍스트 제거
- [08/21] 리스트 태그 붙이기


# Ref.
크롤러 만들기 [참고](https://www.geeksforgeeks.org/web-scraping-from-wikipedia-using-python-a-complete-guide/)