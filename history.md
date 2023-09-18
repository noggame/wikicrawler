
# Patch 예정
- 관련 데이터 링크정보 저장/관리 (연관검색 키워드로 사용 예정)

# Update 내역
[09/18]
- 전체 포맷에 대한 개행문자 처리 수정 (개행문자 삽입 단일화 구조로 수정)
- Table, Description, Code 처리 수정
- CSV (using Pandas) 저장 method 추가
- Link Class 생성 및 적용 (to Sentence & Passage Class)

[09/13]
- Table, List, Description 적용 (Table의 경우 보완 필요)
- 각주, 외부 링크 등 불필요한 Passage 필터링 적용
- 중첩된 구조의 Text 처리 적용 (Recursion) [예시, 리스트 내부의 리스트, 혹은 테이블 내부 리스트 등...]
    - 중첩된 문장의 경우, 중첩 깊이에 따라 문장 앞 여백 적용

[08/21]
- 제목의 "[편집]" 텍스트 제거
- 리스트 태그 붙이기