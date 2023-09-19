# for data processing
import requests
from bs4 import BeautifulSoup
import modules.PassageManager as PM
# for configuration
import configparser
from os import getcwd
import pandas as pd
import logging


class Configuration:
    
    def __init__(self) -> None:
        self.country_code = "ko"
        self.base_url = f"https://{self.country_code}.wikipedia.org"
        self.global_linkset = set()   # link 데이터 중복 확인

        ### Configuration (for config.ini)
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(f"{getcwd()}/config.ini")

        # TODO 설정파일(config.ini)의 값 json 으로 수정
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


# global
CRAWLER_CONFIG = Configuration()


def __remove_meaningless_tag(target:BeautifulSoup, excludeTagList:list=[], excludeClassList:list=[]):
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


def get_raw(keyword:str="", url="") -> BeautifulSoup:
    
    if (keyword and url) or (not keyword and not url):
        logging.warning("Only one param. should be defined from [keyword, url]")
        return None
    
    bs_data = ""
    if keyword:
        raw_data = requests.get(CRAWLER_CONFIG.base_url+f"/wiki/{keyword}")
        bs_data = BeautifulSoup(raw_data.content, "html.parser")
    elif url:
        raw_data = requests.get(f"{url}")
        bs_data = BeautifulSoup(raw_data.content, "html.parser")
    else:
        logging.error("Non-defined error occurs.")
        return None

    return bs_data


def get_text(source:BeautifulSoup, newline_tag:bool=False) -> str:
    """
    입력된 source (html) 데이터로부터 기존 텍스트와 함께 이미지 및 수식 등을 텍스트 정보로 정제해 반환한다.
    """

    result = ""
    margin = 2  # 재귀적으로 호출되는 경우 문장 앞 여백 크기

    if type(source) == str:
        return str(source).strip()

    for src_child in source.children:
        # if source.name == "dd":
        #     print(f">>> {src_child}")


        src_child:BeautifulSoup = src_child
        next_child:BeautifulSoup = src_child.next_sibling


        # case 1) innerText (태그없이 텍스트만 있는 데이터, ~leaf node)
        if not src_child.name:

            if not src_child.get_text(strip=True):  # empty context
                continue

            if not next_child:                      # innerText && leaf node
                result += src_child.get_text().replace("\n", "")

            elif next_child.name:                   # innerText -> tag
                result += src_child.get_text().replace("\n", "")

                # if next_child.get_text().rstrip():
                #     result += src_child.get_text().replace("\n", "")    # FIXME print
            else:                                   # innerText -> innerText
                result += src_child.get_text().replace("\n", " ")   # FIXME print


        # case 2) 개행문자
        elif src_child.name == "br":
            result += "<br/>" if newline_tag else "\n"


        # case 3) 추가 처리가 필요한 태그 - Recursion
        elif src_child.name in CRAWLER_CONFIG._filter.get("available_tag"):
            ### deprecated
            # _tag, _sentence = self.get_sentence(src_child)
            # sentence_with_margin = "".join([f"{' '*margin}{line}\n" for line in _sentence.split("\n") if line]) # append margin to each line
            ###
            _sentence:PM.DataType.Sentence = get_sentence(source=src_child)
            sentence_with_margin = "".join([f"{' '*margin}{line}\n" for line in _sentence.context.split("\n") if line]) # append margin to each line
            result += f"\n{sentence_with_margin.rstrip()}"


        # etc) 수식 확인 및 alttext 추출
        elif src_child.find_all(name="math"):
            mathList = src_child.find_all(name="math")
            result += "".join([math_text.attrs.get('alttext') for math_text in mathList if math_text.has_attr("alttext")]).replace("\displaystyle ", "")


        # not defined
        else:
            result += src_child.get_text()

    return result+"\n"


def get_links(source:BeautifulSoup) -> list:
    """
    입력 source 에서 link 목록 추출 후 Link 객체로 변환 후 전체 목록 반환

    ---
    ## Parameter
    - source:BeaurifulSoup = html raw data

    ---
    ## Return
    List of Link object

    ### Link object is consist of
    - tag : tag 이름
    - sentence : 해당 tag 뒤의 내용 (빈 내용의 경우 "" 반환)
    - links : [List of Link object]
    """
    
    linkList = []
    
    linkSourceList = source.find_all(name="a")
    for linkSource in linkSourceList:
        linkSource:BeautifulSoup = linkSource
        
        keyword = linkSource.get_text(strip=True)
        url = linkSource.get("href") or []

        if keyword and url:
            linkObj = PM.DataType.Link(keyword=keyword, url=url)
            linkList.append(linkObj)

    return linkList


def get_sentence(source:BeautifulSoup, tag_marking:bool=True):
    """
    입력 source 에 대한 태그 분석 뒤, 구분 태그명과 내용을 반환

    ---
    ## Parameter
    - source:BeaurifulSoup = html raw data
    - tag_marking:bool = 각 문장의 접두어(태그) 삽입여부

    ---
    ## Return
    Sentence

    ### Sentence object is consist of
    - tag : tag 이름
    - context : 해당 tag 뒤의 내용 (빈 내용의 경우 "" 반환)
    - links : [List of Link object]
    """

    tag:PM.DataType.Tag = None
    sentence:PM.DataType.Sentence = None

    # TODO Links 데이터 추출하는 함수 정의 및 적용
    # TODO Sentence 반환


    ### Hearder <h1> to <h6>
    if source.name in ["h1", "h2"]:
        tag = PM.DataType.Tag.get_header_by_tagname(source.name)
        context = f"{get_text(source).strip()}"
        links = get_links(source=source)

        sentence = PM.DataType.Sentence(tag=tag, context=context, links=links)

    elif source.name in ["h3", "h4", "h5", "h6"]:
        tag = PM.DataType.Tag.get_header_by_tagname(source.name)
        tag_str = f"{CRAWLER_CONFIG._identifier.get('title')}"*int(source.name[1])+" " if tag_marking else ""
        context = f"{tag_str}{get_text(source).strip()}\n"
        links = get_links(source=source)

        sentence = PM.DataType.Sentence(tag=tag, context=context, links=links)


    ### List <ul>
    elif source.name == "ul":
        ul_text = ""
        tag_str = f"{CRAWLER_CONFIG._identifier.get('list')} "
        for li in source.children:
            li:BeautifulSoup = li
            if li.name == "li":
                ul_text += f"{tag_str}{get_text(li)}"

        tag = PM.DataType.Tag.LIST
        context = ul_text
        links = get_links(source=source)

        sentence = PM.DataType.Sentence(tag=tag, context=context, links=links)


    ### List - Ordered <ol>
    elif source.name == "ol":
        ol_text = ""
        numbering_idx = 1
        for li in source.children:
            li:BeautifulSoup = li
            if li.name == "li":
                ol_text += f"{numbering_idx}. {get_text(li)}" if tag_marking else f"{get_text(li)}"
                numbering_idx += 1

        tag = PM.DataType.Tag.LIST
        context = ol_text
        links = get_links(source=source)

        sentence = PM.DataType.Sentence(tag=tag, context=context, links=links)


    ### Description List
    # <dl>, <dt>&<dd> 순으로 처리
    elif source.name == "dl":
        description = ""     # markdown format

        # description title & data
        for eachDesc in source.children:
            eachDesc:BeautifulSoup = eachDesc

            if eachDesc.name in ["dt", "dd"]:
                description += get_text(eachDesc)
            else:
                description += get_text(description)
            # description += "\n"

        tag = PM.DataType.Tag.DESCRIPTION
        tag_str = f"{CRAWLER_CONFIG._identifier.get('description')}"*3 + "\n"
        context = f"{tag_str}{description}{tag_str}" if tag_marking else description
        links = get_links(source=source)

        sentence = PM.DataType.Sentence(tag=tag, context=context, links=links)


    ### Table
    # <tr> <th> <td> 순으로 처리
    elif source.name == "table":
        table_markdown = ""     # markdown format
        tag_table_divider = f"{CRAWLER_CONFIG._identifier.get('table')}"

        ### table 중 class 속성값으로 wikitable을 가지는 테이블만 처리
        # if "wikitable" not in source.get_attribute_list("class"):
        #   continue
        ###

        # Table Row
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
                    ns = col_child.next_sibling

                    # case 1) innerText 이후 다음 데이터와 구분을 위해 개행문자가 들어가 있는 경우
                    if not col_child.name:    # innerText
                        
                        if not col_child.get_text(strip=True):      # empty context
                            continue

                        # innerText && leaf node
                        if not ns:
                            table_markdown += col_child.get_text().replace("\n", "")
                        # innerText -> tag
                        elif ns.name:
                            table_markdown += col_child.get_text().replace("\n", "")
                        # innerText -> innerText
                        else:
                            table_markdown += col_child.get_text().replace("\n", " ")


                    # case 2) 개행문자를 인위적으로 삽입한 경우
                    elif col_child.name == "br":
                        table_markdown += "<br>"


                    # case 3) Tag 내부의 Text 추출
                    else:
                        table_markdown += get_text(col_child, newline_tag=True).replace("\n", "")

                table_markdown += f"{tag_table_divider}"    # end of each column

            table_markdown += "\n"  # end of each row

        tag = PM.DataType.Tag.TABLE
        context = table_markdown.strip()
        links = get_links(source=source)

        sentence = PM.DataType.Sentence(tag=tag, context=context, links=links)


    ### Blockquote
    # need to implement...
    ###


    ### Code
    # <pre> 에 대한 처리
    elif source.name == "pre":
        tag = PM.DataType.Tag.CODE
        tag_str = f"{CRAWLER_CONFIG._identifier.get('code')}"*3 + "\n"
        context = f"{tag_str}{source.get_text().strip()}{tag_str}".strip()
        links = get_links(source=source)

        sentence = PM.DataType.Sentence(tag=tag, context=context, links=links)


    ### Others (~context, ~text)
    else:
        tag = PM.DataType.Tag.CONTEXT
        context = get_text(source=source)
        links = get_links(source=source)

        sentence = PM.DataType.Sentence(tag=tag, context=context, links=links)

    return sentence


def get_passages_from(keyword:str="", url:str="", depth:int=0):
    """
    입력된 keyword를 기반으로 wikipedia에서 검색하고, 해당 정보를 문단별로 Passage List 형태로 반환

    ## Parameter
    keyword : str = 검색어
    """

    # get raw(html) data
    bs_data:BeautifulSoup = get_raw(keyword=keyword, url=url)
    if not bs_data:
        logging.error("Wikipedia request error.")
        return None

    main = bs_data.find(name="main")
    body_div = main.select_one("#mw-content-text > div.mw-parser-output")   # get body

    # extract keyword
    header_keyword = bs_data.find(name="h1", attrs={"id": "firstHeading"}).get_text().strip()
    
    sentence_keyword = PM.DataType.Sentence(tag=PM.DataType.Tag.HEADER_1, context=header_keyword, links=[])
    sentenceList = [sentence_keyword]

    # pre-processing : 처리가 불필요한 정보 제거
    __remove_meaningless_tag(body_div, excludeTagList=CRAWLER_CONFIG._filter.get("exclude_tag"), excludeClassList=CRAWLER_CONFIG._filter.get("exclude_class"))

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

            if eachData.name in CRAWLER_CONFIG._filter.get("available_tag"):
                sentence:PM.DataType.Sentence = get_sentence(eachData)

                if sentence.context:
                    sentenceList.append(sentence)

    passageList = PM.make_passages_from_sentences(sentenceList=sentenceList)

    # post-processing : 학습/시험에 관계없는 패시지 제외 (h2 태그로 판별)
    passageList = [p for p in passageList if p.title not in CRAWLER_CONFIG._filter.get("exclude_passage")]

    # get additional passageList using recursion
    if depth > 3:
        logging.warning("Depth should be set between 0 and 3")
    elif depth > 0:
        additionalPassageList = []
        for passage in passageList:
            passage:PM.DataType.Passage = passage

            for link in passage.links:
                link:PM.DataType.Link = link
                if not link.url.startswith("/wiki/") or (link.url in CRAWLER_CONFIG.global_linkset):
                    continue

                # Print
                import urllib.parse as up
                print(f'{passage.keyword} --- {up.unquote(link.url, encoding="utf-8-sig")}')

                CRAWLER_CONFIG.global_linkset.add(link.url)
                link_url = f"{CRAWLER_CONFIG.base_url}{link.url}"
                
                additionalPassageList.extend(get_passages_from(url=link_url, depth=(depth-1)))

        passageList.extend(additionalPassageList)

    return passageList


def save_to_csv(passageList:list, filepath:str):
    outputDataFrame = []  # set header

    for passage in passageList:
        try:    # type check
            passage:PM.DataType.Passage = passage
        except TypeError as te:
            print(f"passage list is not composed of Passage object.[DETAIL]\n{te}")
            exit(1)

        keyword = passage.keyword or ""
        title = passage.title or ""
        contents = passage.contents or ""
        links = "\n".join([f"{link.keyword}({link.url})" for link in passage.links])

        outputDataFrame.append([keyword, title, contents, links])

    storeDataFrame = pd.DataFrame(data=outputDataFrame, columns=["keyword", "title", "contents", "links"])
    print(storeDataFrame.describe())
    storeDataFrame.to_csv(filepath)
