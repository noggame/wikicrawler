# for data processing
import requests
from bs4 import BeautifulSoup
import modules.PassageManager as PM
# for configuration
import configparser
from os import getcwd

class WikiCrawler:
    ### Configuration
    available_tag = ["h1", "h2", "h3", "h4", "h5", "h6",
                     "p", "ul", "ol"]
    # available_tag = ["h1", "h2", "h3", "h4", "h5", "h6",
    #                  "p", "ul", "ol", "table"]

    ### Operations
    def __init__(self) -> None:
        self._country_code = "ko"
        self._url = f"https://{self._country_code}.wikipedia.org/wiki"

        # from Config file
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(f"{getcwd()}/config.ini")

        self._tag = {
            "title" : f"{config.get('tag', 'title')}",
            'list' : f"{config.get('tag', 'list')}"
        }
        self._unnecessary_title = [item.strip() for item in config.get('filter', 'unnecessary_title').split(",")]

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
        # "[편집]" 포맷의 링크 텍스트 제거
        editSpanList = target.find_all(attrs={"class": "mw-editsection"})
        for editSpan in editSpanList:
            editSpan.decompose()


    def get_raw(self, keyword:str) -> BeautifulSoup:

        raw_data = requests.get(self._url+f"/{keyword}")
        bs_data = BeautifulSoup(raw_data.content, "html.parser")

        return bs_data
    

    def make_passage(self, keyword:str):
        """
        입력된 keyword를 기반으로 wikipedia에서 검색하고, 해당 정보를 문단별로 Passage List 형태로 반환

        ## Parameter
        keyword : str = 검색어
        """

        sentence_keyword = PM.DataType.Sentence(tag=PM.DataType.Tag.HEADER_1, context=keyword)
        sentenceList = [sentence_keyword]

        # get raw(html) data
        bs_data:BeautifulSoup = self.get_raw(keyword=keyword)
        main = bs_data.find(name="main")
        body_div = main.select_one("#mw-content-text > div.mw-parser-output")   # get body

        # TODO 링크 목록 추출/저장

        # pre-processing
        self._remove_meaningless_tag_(body_div)

        # body의 컨텐츠 순차 처리
        for child in body_div.children:
            child:BeautifulSoup = child # type converting/check

            # 태그별 분류&처리
            if child.name in self.available_tag:
                tag, text = self.extract_sentence(child)

                if not text:
                    continue

                sentence = PM.DataType.Sentence(tag=tag, context=text)
                sentenceList.append(sentence)

            elif child.name == "meta":
                for grandChild in child:
                    if grandChild.name in self.available_tag:
                        tag, text = self.extract_sentence(grandChild)
                        if text:
                            sentence = PM.DataType.Sentence(tag=tag, context=text)
                            sentenceList.append(sentence)

        
        passageList = PM.make_passages_from_sentences(sentenceList=sentenceList)
        # print(*passageList, sep="\n")

        for passage in passageList:
            passage:PM.DataType.Passage = passage
            print(f"[Title] {passage.title}")
            print(f"[Keyword] {passage.keyword}")
            print(f"[Contents] {passage.contents}")
            print("-"*30)

        ### post-processing
        # TODO 1. 불필요한 정보 필터링
        # TODO 2. sentence list 로부터 Passage 생성


    def extract_sentence(self, target:BeautifulSoup, tag:bool=False):
        """
        입력 target 문장에 대한 태그 분석 뒤, 구분 태그명과 내용을 반환

        ---
        ## Parameter
        - target:bs = html raw data
        - tag:bool = 각 문장의 접두어(태그) 삽입여부
        ---
        ## Return
        tuple(tag, sentence)
        - tag : tag 이름
        - sentence : 해당 tag 뒤의 내용 (빈 내용의 경우 "" 반환)
        """
        tag = ""
        sentence = ""

        # 1) Hearder
        if target.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            tag = PM.DataType.Tag.get_header_by_tagname(target.name)
            sentence = target.get_text().strip()

        # 2) List
        elif target.name == "ul":
            ul_text = ""
            for li in target.children:
                li:BeautifulSoup = li
                if li.name == "li":
                    ul_text += f"{li.get_text().strip()}\n"

                    ### with '-' tag
                    # li_tag = f"{self.list_tag}"
                    # ul_text += f"{li_tag} {li.get_text().strip()}\n"  

            tag = PM.DataType.Tag.LIST
            sentence = ul_text.strip()

        # 3) Table


        # ETC) Others (~context, ~text)
        else:
            tag = PM.DataType.Tag.CONTEXT
            sentence = target.get_text().strip()

        return tag, sentence


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

