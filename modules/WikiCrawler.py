import requests
from bs4 import BeautifulSoup
from modules.Tag import TagType

from dataclasses import dataclass
@dataclass
class Passage:
    """
    keyword = 페이지 핵심 키워드
    title = 패시지 핵심 키워드
    contents = 패시지 내용
    """
    keyword:str = None
    title:str = None
    contents:str = None


class WikiCrawler:
    title_tag = "="
    list_tag = "-"
    available_tag = ["p", "ul", "ol", 
                     "h1", "h2", "h3", "h4", "h5", "h6"]
    unnecessary_tag = ["table"]
    unnecessary_title = ["각주"]    # FIXME : 영어도 고려해야됨


    def __init__(self) -> None:
        self._country_code = "ko"
        self._url = f"https://{self._country_code}.wikipedia.org/wiki"

    def _set_base_(self, country_code:str="ko"):
        """
        country_code = 위키 검색엔진 국가코드 입력
        """
        if not country_code:
            country_code = self._country_code

    def _remove_meaningless_tag_(self, target:BeautifulSoup):
        """
        불필요한 태그 삭제
        """

        # <sup>
        # "[n]" 형태의 각주 텍스트 제거
        supList = target.find_all(name="sup")
        for sup in supList:
            sup.decompose()

        # <span class="mw-editsection">
        # "[편집]" 형태의 링크 텍스트 제거
        editSpanList = target.find_all(attrs={"class": "mw-editsection"})
        for editSpan in editSpanList:
            editSpan.decompose()


    def get_raw(self, keyword:str):

        raw_data = requests.get(self._url+f"/{keyword}")
        bs_data = BeautifulSoup(raw_data.content, "html.parser")

        return bs_data
    

    # TODO : contents 대신 헤더마다 패시지 단위로 쪼개서 반환
    def get_content(self, keyword:str):
        contents = [f"{self.title_tag}{keyword}{self.title_tag}"]       # init. with keyword used search
        # passage = None

        bs_data:BeautifulSoup = self.get_raw(keyword=keyword)
        main = bs_data.find(name="main")

        body_div = main.select_one("#mw-content-text > div.mw-parser-output")   # get body
        self._remove_meaningless_tag_(body_div)

        # body의 컨텐츠 순차 처리
        for child in body_div.children:

            # 태그별 분류&처리
            if child.name in self.available_tag:
                text, tag = self.get_tag_from(child)
                if not text:
                    continue

                # if tag == Tag.HEAD:
                #     passage = Passage(keyword=keyword, title=text)
                # else:
                #     passage.contents = text

                contents.append(text)
                    # contents.append(f"{len(text)} >> {text}")

            elif child.name == "meta":
                for grandChild in child:
                    if grandChild.name in self.available_tag:
                        text, tag = self.get_tag_from(grandChild)
                        if text:
                            contents.append(text)
                            # contents.append(f"{len(text)} >> {text}")


        ### TODO : 후처리 (불필요한 정보 제거[타이틀 보고 판단?])

        print(*contents, sep="\n")


    def get_tag_from(self, target:BeautifulSoup):
        """
        입력 target 문장에 대해 태그를 붙이고, 어떤 태그를 붙였는지와 함께 정보 반환
        
        RETURN Str : 태그를 붙인 문장
        RETURN Tag : 구분 태그
        """

        if target.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            return f"{target.get_text().strip()}", TagType.HEADER
            # return f"{title_tag}{target.get_text().strip()}{title_tag}", Tag.HEAD
        elif target.name == "ul":
            # 하위 각 list item(li) 시작부에 태그를 붙인다.
            ul_text = ""
            li_tag = f"{self.list_tag}"

            for li in target.children:
                if li.name == "li":
                    ul_text += f"{li_tag}{li.get_text().strip()}\n"

            return f"{ul_text}".strip(), TagType.LIST
        else:
            return target.get_text().strip(), TagType.NONE




    # TODO : 구현필요
    def get_categories(self):
        """
        문서 하단의 카테고리 정보 추출
        """

        # 1. div id=catlink 인 태그 추출
        pass


    # TODO: 구현 필요
    def get_keyword_with_link(self):
        """
        문서내 Contents에서 링크가 있는 키워드와 그 링크 url 정보를 함께 반환
        목적 : 재귀적으로 데이터 탐색

        ---
        # 데이터 구조 (계획)
        = {id, title, contents, parent}

        id : 해당 데이터 고유 id
        title : h테그가 붙은 제목 정보
        contents : h태그에 대한 설명/본문 내용
        parent : 상위 h태그 id
        ---

        """

        

        pass

