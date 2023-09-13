from enum import Enum
import logging

class Tag(Enum):
    """
    NONE = 0\n
    LIST = 2
    HEADER_N = 11~16 (N:1~6)\n
    """

    NONE = 0
    CONTEXT = 1
    LIST = 2
    TABLE = 3
    CODE = 4
    DESCRIPTION = 5
    # Header
    HEADER_BASE = 100
    HEADER_1 = HEADER_BASE + 1   # keyword
    HEADER_2 = HEADER_BASE + 2   # Passage divider
    HEADER_3 = HEADER_BASE + 3
    HEADER_4 = HEADER_BASE + 4
    HEADER_5 = HEADER_BASE + 5
    HEADER_6 = HEADER_BASE + 6

    def get_header_by_tagname(tagName:str):
        if tagName in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            return Tag(Tag.HEADER_BASE.value+int(tagName[1]))
        else:
            logging.warning("not found header by tagName")
            return None
        
    def is_passage_header(tag:int):
        """
        passage 구분을 위해 사용되는 헤더인지 확인

        ---
        ## Return
        h1, h2 tag인 경우 True 반환, 이 외의 경우에는 False 반환
        """

        # return True if (Tag.HEADER_1 <= tag and tag <= Tag.HEADER_6) else False
        return True if (tag == Tag.HEADER_1 or tag == Tag.HEADER_2) else False
    
        
class Sentence:
    def __init__(self, tag:Tag, context:str) -> None:
        self._tag = tag
        self._context = context

    # Getter/Setter
    @property
    def tag(self) -> Tag:
        return self._tag
    @property
    def context(self) -> str:
        return self._context
    @tag.setter
    def tag(self, tag:Tag):
        self._tag = tag
    @context.setter
    def context(self, context:str):
        self._context = context

    def __str__(self) -> str:
        return f"(tag:{self.tag.name}, context:{self.context})"
    
class Passage:
    """
    패시지 정보를 담고있는 객체

    ---
    ## PARAM
    - title : str = 제목
    - contents : str = 내용
    - keyword : str = 어떤 keyword 검색에서 추출된 passage인지 출처
    """

    def __init__(self, title:str="", contents:str="", keyword:str="") -> None:
        self._title = title
        self._contents = contents
        self._keyword = keyword

    # Getter/Setter
    @property
    def title(self) -> str:
        return self._title #if self._title else None
    @property
    def contents(self) -> str:
        return self._contents #if self._contents else None
    @property
    def keyword(self) -> str:
        return self._keyword #if self._keyword else None
    @title.setter
    def title(self, title):
        self._title = title
    @contents.setter
    def contents(self, contents):
        self._contents = contents
    @keyword.setter
    def keyword(self, keyword):
        self._keyword = keyword

    def __str__(self) -> str:
        printFormat = "-"*30
        printFormat += f"\n[Title] {self.title}"
        printFormat += f"\n[Keyword] {self.keyword}"
        printFormat += f"\n[Contents] {self.contents}"
        
        return printFormat
    