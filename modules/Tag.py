from bs4 import BeautifulSoup
from enum import Enum

class TagType(Enum):
    NONE = 0
    HEADER = 1
    LIST = 2

def classify(target:BeautifulSoup):
    """
    입력 target 문장에 대해 태그를 붙이고, 어떤 태그를 붙였는지와 함께 정보 반환

    @param target = 구분 대상
    
    @RET. (Str = 태그를 붙인 문장, Tag = 구분 태그)
    """

    ### Header
    if target.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        return f"{target.get_text().strip()}", TagType.HEADER
        # return f"{title_tag}{target.get_text().strip()}{title_tag}", Tag.HEAD


    ### List
    elif target.name == "ul":
        list_contents = ""

        # 하위 각 list item(li) 시작부에 태그를 붙인다.
        for li in target.children:
            if li.name == "li":
                list_contents += f"{li.get_text().strip()}\n"
                # ul_text += f"{li_tag}{li.get_text().strip()}\n"

        return f"{list_contents}".strip(), TagType.LIST
    

    ### Others
    else:
        return target.get_text().strip(), TagType.NONE

