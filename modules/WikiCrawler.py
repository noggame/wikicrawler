# for data processing
import requests
from bs4 import BeautifulSoup
import modules.PassageManager as PM
# for configuration
import configparser
from os import getcwd

class WikiCrawler:
    
    def __init__(self) -> None:
        self._country_code = "ko"
        self._url = f"https://{self._country_code}.wikipedia.org/wiki"

        ### Configuration (for config.ini)
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(f"{getcwd()}/config.ini")

        self._identifier = {
            'title' : f"{config.get('identifier', 'title')}",
            'list' : f"{config.get('identifier', 'list')}",
            'table' : f"{config.get('identifier', 'table')}",
            'code' : f"{config.get('identifier', 'code')}"
        }
        self._available_tag = [item.strip() for item in config.get('filter', 'available_tag').split(",")]
        self._unnecessary_title = [item.strip() for item in config.get('filter', 'unnecessary_title').split(",")]


    ### Operations
    def _set_base_(self, country_code:str="ko"):
        """
        country_code = 위키 검색엔진 국가코드 입력
        """
        if not country_code:
            country_code = self._country_code


    def get_raw(self, keyword:str) -> BeautifulSoup:

        raw_data = requests.get(self._url+f"/{keyword}")
        bs_data = BeautifulSoup(raw_data.content, "html.parser")

        return bs_data
    

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

            dataQueue = []

            # 예외적인 태그들 처리를 위해 dataQueue에 처리해야하는 대상들 선별/추가
            if child.name == "meta":
                for grandChild in child.children:
                    if grandChild.name == "div":
                        dataQueue.extend(grandChild.children)
                    else:
                        dataQueue.append(grandChild)
            else:
                dataQueue.append(child)

            # 태그별 분류&처리
            for eachData in dataQueue:
                eachData:BeautifulSoup = eachData

                if eachData.name in self._available_tag:
                    tag, text = self.extract_sentence(eachData)
                    if text:
                        sentence = PM.DataType.Sentence(tag=tag, context=text)
                        sentenceList.append(sentence)

        passageList = PM.make_passages_from_sentences(sentenceList=sentenceList)

        ### print
        for passage in passageList:
            passage:PM.DataType.Passage = passage
            print(f"[Title] {passage.title}")
            print(f"[Keyword] {passage.keyword}")
            print(f"[Contents] {passage.contents}")
            print("-"*30)

        return passageList

        ### post-processing
        # TODO 1. 불필요한 정보 필터링
        # TODO 2. sentence list 로부터 Passage 생성


    def extract_sentence(self, source:BeautifulSoup, tag:bool=False):
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
        if source.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            tag = PM.DataType.Tag.get_header_by_tagname(source.name)
            tag_str = f"{self._identifier.get('title')}"*int(source.name[1])
            sentence = f"{tag_str} {source.get_text().strip()}"

        # 2) List
        elif source.name == "ul":
            ul_text = ""
            for li in source.children:
                li:BeautifulSoup = li
                if li.name == "li":
                    ul_text += f"{self._identifier.get('list')} {li.get_text().strip()}\n"

                    ### with '-' tag
                    # li_tag = f"{self.list_tag}"
                    # ul_text += f"{li_tag} {li.get_text().strip()}\n"  

            tag = PM.DataType.Tag.LIST
            sentence = ul_text.strip()

        # 3) Table
        # <tr> <th> <td> 순으로 처리
        elif source.name == "table":
            table_markdown = ""     # markdown format

            ## table 중 class 속성값으로 wikitable을 가지는 테이블만 처리
            if "wikitable" in source.get_attribute_list("class"):

                # Table Row
                for row in source.find_all(name="tr"):
                    row:BeautifulSoup = row
                    table_markdown += f"{self._identifier.get('table')}"

                    # Table Head & Data
                    thdList = []
                    thdList.extend(row.find_all(name="th"))
                    thdList.extend(row.find_all(name="td"))

                    for col in thdList:
                        col:BeautifulSoup = col
                        for text_componet in col.children:
                            if text_componet.name == "br":
                                table_markdown += "<br/>"
                            else:
                                table_markdown += text_componet.get_text().replace("\n", "")
                        table_markdown += f"{self._identifier.get('table')}"

                    table_markdown += "\n"

            tag = PM.DataType.Tag.TABLE
            sentence = table_markdown.strip()

        
        # 4) Code
        # <pre> 에 대한 처리
        elif source.name == "pre":
            code_divider = f"{self._identifier.get('code')}"*3
            
            tag = PM.DataType.Tag.CODE
            sentence = f"{code_divider}\n{source.get_text().strip()}\n{code_divider}"

        # ETC) Others (~context, ~text)
        else:
            tag = PM.DataType.Tag.CONTEXT
            sentence = source.get_text().strip()

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

