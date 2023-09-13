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
            'code' : f"{config.get('identifier', 'code')}",
            'description' : f"{config.get('identifier', 'description')}"
        }

        self._filter = {
            'available_tag' : [item.strip() for item in config.get('filter', 'available_tag').split(",")],
            'exclude_tag' : [item.strip() for item in config.get('filter', 'exclude_tag').split(",")],
            'exclude_class' : [item.strip() for item in config.get('filter', 'exclude_class').split(",")],
            'exclude_passage' : [item.strip() for item in config.get('filter', 'exclude_passage').split(",")]
        }


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
    

    def get_text(self, source:BeautifulSoup) -> str:
        """
        입력된 source (html) 데이터로부터 기존 텍스트와 함께 이미지 및 수식 등을 텍스트 정보로 정제해 반환한다.
        """

        # img -> alt
        # math -> alttext

        result = ""

        # 하위 태그들 중 이미지/특수기호 등이 있다면, 해당 문자는 별도로 분리해 처리
        for tag in source.children:
            tag:BeautifulSoup = tag

            if not tag.name:        # leaf node
                result += tag.get_text().replace("\n", " ")
            else:
                ### TODO 재귀적 처리
                
                # 이미지가 존재하는 태그는 img내 alt 속성에 정의된 text를 추출해 사용, 이 외는 단순 text 출력
                imageList = tag.find_all(name="img")
                if imageList:
                    result += "".join([img.attrs.get('alt') for img in imageList if img.has_attr("alt")])
                else:
                    result += tag.get_text().replace("\n", " ")

        return result.strip()
    

    def _remove_meaningless_tag(self, target:BeautifulSoup, excludeTagList:list=[], excludeClassList:list=[]):
        """
        불필요한 태그 삭제
        """
        ### 예외 태그 예시
        # <sup> : [n] 형태의 각주

        # exclude tag
        for exTag in excludeTagList:
            exTagList = target.find_all(name=exTag)
            for et in exTagList:
                et.decompose()

        ### 예외 클래스 예시
        # mw-editsection : "[편집]" 포맷의 링크 텍스트 제거
        # mwe-math-mathml-a11y : 수학기호 이미지 제거
        for exCls in excludeClassList:
            exClsList = target.find_all(attrs={"class": exCls})
            for ec in exClsList:
                ec.decompose()


    def extract_sentence(self, source:BeautifulSoup, tag_marking:bool=True):
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

        ### Hearder
        if source.name in ["h1", "h2"]:
            tag = PM.DataType.Tag.get_header_by_tagname(source.name)
            sentence = f"{self.get_text(source)}"
        elif source.name in ["h3", "h4", "h5", "h6"]:
            tag = PM.DataType.Tag.get_header_by_tagname(source.name)
            tag_str = f"{self._identifier.get('title')}"*int(source.name[1])+" " if tag_marking else ""
            sentence = f"{tag_str}{self.get_text(source)}"


        ### List
        elif source.name == "ul":
            ul_text = ""
            tag_str = f"{self._identifier.get('list')} "
            for li in source.children:
                li:BeautifulSoup = li
                if li.name == "li":
                    ul_text += f"{tag_str}{self.get_text(li)}\n"

            tag = PM.DataType.Tag.LIST
            sentence = ul_text.strip()


        ### List - Ordered
        elif source.name == "ol":
            ol_text = ""
            numbering_idx = 1
            for li in source.children:
                li:BeautifulSoup = li
                if li.name == "li":
                    ol_text += f"{numbering_idx}. {self.get_text(li)}\n" if tag_marking else f"{self.get_text(li)}\n"
                    numbering_idx += 1

            tag = PM.DataType.Tag.LIST
            sentence = ol_text.strip()


        ### Description List
        # <dl>, <dt>&<dd> 순으로 처리
        elif source.name == "dl":
            description = ""     # markdown format

            # description title & data
            for eachDesc in source.children:
                eachDesc:BeautifulSoup = eachDesc

                if eachDesc.name in ["dt", "dd"]:
                    for descItem in eachDesc:
                        descItem:BeautifulSoup = descItem

                        # case 1) Text 와 태그가 연이어 나오는 경우에는 구분을 위해 개행문자가 들어가 있으나 실제로는 이어진 문장
                        if not descItem.name:
                            if descItem.next_sibling and descItem.next_sibling.name:
                                description += descItem.get_text().strip()
                            else:
                                description += descItem.get_text() + "\n"
                        # case 2) 패턴1 에서 인위적으로 개행문자를 삽입하려는 경우 br 태그가 사용됨
                        elif descItem.name == "br":
                            description += "\n"
                        # case 3) 태그 내부에 삽입된 Text
                        else:
                            description += self.get_text(descItem)

                else:
                    description += self.get_text(description)
                description += "\n"

            tag = PM.DataType.Tag.DESCRIPTION
            tag_str = f"{self._identifier.get('description')}"*3 + "\n"
            sentence = f"{tag_str}{description}{tag_str}" if tag_marking else description


        ### Table
        # <tr> <th> <td> 순으로 처리
        elif source.name == "table":
            table_markdown = ""     # markdown format
            tag_table_divider = f"{self._identifier.get('table')}"

            # Table Row
            # if "wikitable" in source.get_attribute_list("class"):     # table 중 class 속성값으로 wikitable을 가지는 테이블만 처리
            for row in source.find_all(name="tr"):
                row:BeautifulSoup = row
                table_markdown += f"{tag_table_divider}"

                # Table Head & Data
                descList = []
                descList.extend(row.find_all(name="th"))
                descList.extend(row.find_all(name="td"))

                for col in descList:
                    col:BeautifulSoup = col
                    for col_child in col.children:
                        # case 1) 개행문자를 인위적으로 삽입한 경우
                        if col_child.name == "br":
                            table_markdown += "<br/>"
                        # case 2) innerText 이후 다음 데이터와 구분을 위해 개행문자가 들어가 있는 경우
                        elif not col_child.name:    # innerText
                            
                            if not col_child.get_text():    # empty context
                                continue

                            ns = col_child.next_sibling
                            if not ns:      # innerText == leaf node
                                table_markdown += col_child.get_text().rstrip()
                            elif ns.name:   # innerText -> tag
                                if ns.get_text().strip():
                                    table_markdown += col_child.get_text()
                            else:           # innerText -> innerText
                                table_markdown += col_child.get_text()
                        # case 3) Tag 내부의 Text 추출
                        else:
                            table_markdown += self.get_text(col_child)

                    table_markdown += f"{tag_table_divider}"    # end of each column

                table_markdown += "\n"  # end of each row

            tag = PM.DataType.Tag.TABLE
            sentence = table_markdown.strip()

        ### Blockquote

        ### Code
        # <pre> 에 대한 처리
        elif source.name == "pre":
            tag_str = f"{self._identifier.get('code')}"*3 + "\n"
            
            tag = PM.DataType.Tag.CODE
            sentence = f"{tag_str}{source.get_text().strip()}{tag_str}".strip()

        ### Others (~context, ~text)
        else:
            tag = PM.DataType.Tag.CONTEXT
            sentence = self.get_text(source=source)

        return tag, sentence




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

        # pre-processing : 처리가 불필요한 정보 제거
        self._remove_meaningless_tag(body_div, excludeTagList=self._filter.get("exclude_tag"), excludeClassList=self._filter.get("exclude_class"))

        # body의 컨텐츠 순차 처리
        for child in body_div.children:
            child:BeautifulSoup = child # type converting/check

            # 예외적인 태그들 처리를 위해 dataQueue에 처리해야하는 대상들 선별/추가
            dataQueue = []
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

                if eachData.name in self._filter.get("available_tag"):
                    tag, text = self.extract_sentence(eachData)
                    if text:
                        sentence = PM.DataType.Sentence(tag=tag, context=text)
                        sentenceList.append(sentence)

        passageList = PM.make_passages_from_sentences(sentenceList=sentenceList)

        # post-processing : 학습/시험에 관계없는 패시지 제외 (h2 태그로 판별)
        passageList = [passage for passage in passageList if passage.title not in self._filter.get("exclude_passage")]

        return passageList

