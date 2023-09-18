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
    LINK = 6
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
    
class Link:
    def __init__(self, keyword:str="", url:str="") -> None:
        self.__keyword = keyword
        self.__url = url

    @property
    def keyword(self):
        return self.__keyword
    @property
    def url(self):
        return self.__url
    @keyword.setter
    def keyword(self, keyword):
        self.__keyword = keyword
    @url.setter
    def url(self, url):
        self.__url = url

    def __str__(self) -> str:
        return f"(keyword:{self.keyword}, url:{self.url})"
    
        
class Sentence:
    def __init__(self, tag:Tag="", context:str="", links:list=[]) -> None:
        self.__tag = tag
        self.__context = context
        self.__links = links

    # Getter/Setter
    @property
    def tag(self) -> Tag:
        return self.__tag
    @property
    def context(self) -> str:
        return self.__context
    @property
    def links(self) -> list:
        return self.__links
    @tag.setter
    def tag(self, tag:Tag):
        self.__tag = tag
    @context.setter
    def context(self, context:str):
        self.__context = context
    @links.setter
    def links(self, links:list):
        self.__links = links

    def __str__(self) -> str:
        return f"(tag:{self.tag.name}, context:{self.context}), links:{self.links}"
    
class Passage:
    """
    패시지 정보를 담고있는 객체

    ---
    ## PARAM
    - title : str = 제목
    - contents : str = 내용
    - keyword : str = 어떤 keyword 검색에서 추출된 passage인지 출처
    """

    def __init__(self, title:str="", contents:str="", keyword:str="", links:list=[]) -> None:
        self.__title = title
        self.__contents = contents
        self.__keyword = keyword
        self.__links = links

    # Getter/Setter
    @property
    def title(self) -> str:
        return self.__title #if self._title else None
    @property
    def contents(self) -> str:
        return self.__contents #if self._contents else None
    @property
    def keyword(self) -> str:
        return self.__keyword #if self._keyword else None
    @property
    def links(self) -> list:
        return self.__links
    @title.setter
    def title(self, title):
        self.__title = title
    @contents.setter
    def contents(self, contents):
        self.__contents = contents
    @keyword.setter
    def keyword(self, keyword):
        self.__keyword = keyword
    @links.setter
    def links(self, links:list):
        self.__links = links

    def __str__(self) -> str:
        printFormat = "-"*30
        printFormat += f"\n[Title] {self.title}"
        printFormat += f"\n[Keyword] {self.keyword}"
        printFormat += f"\n[Contents]\n{self.contents}"
        printFormat += f"\n[Links]\n"

        for link in self.links:
            printFormat += f"{link}\n"
        
        return printFormat
    