"""
여러 패시지 정보를 저장하고, 제어/관리를 위한 객체
"""

import modules.DataType as DT

class DataType:
    Passage = DT.Passage
    Sentence = DT.Sentence
    Tag = DT.Tag
    Link = DT.Link


def make_passages_from_sentences(sentenceList:list):
    """
    순차적으로 입력된 sentenceList를 분석해 Header를 기준으로 패시지 생성

    ---
    ## Parameter
    sentenceList : list<Sentence> = Sentence 객체 리스트

    ## Return
    passageList : list<Passage> = Header로 구분된 Passage 객체 리스트
    """

    passageList = []

    stackedSentence:DataType.Passage = DataType.Passage(links=[])
    # stackedSentence.__init__()
    keyword = ""
    
    # Header1, Header2 기준으로 Sentence를 합쳐 하나의 Passage로 구성
    for curSentence in sentenceList:
        curSentence:DataType.Sentence = curSentence

        # Header 데이터 (Passage 구분자)
        if DataType.Tag.is_passage_header(curSentence.tag):
            if not stackedSentence.title:       # Keyword Header (문서에서 처음 나오는 Header)
                keyword = stackedSentence.title = curSentence.context
                stackedSentence.keyword = keyword       # (self keywording)
            
            else:                               # Sub Header (Key Header 이후의 Header) >> 현재까지 정보 저장 후 초기화
                stackedSentence.contents = stackedSentence.contents.strip()
                passageList.append(stackedSentence)
                
                stackedSentence = DataType.Passage(title=curSentence.context, keyword=keyword, links=[])  # init.

        # 이 외의 데이터
        else:
            stackedSentence.contents += curSentence.context
            stackedSentence.links.extend(curSentence.links)

    else:
        # 마지막 Passage 추가
        stackedSentence.contents = stackedSentence.contents.strip()
        passageList.append(stackedSentence)

    return passageList

# class PassageManager:
#     def __init__(self) -> None:
#         self._passageList = []

#     def add_passge(self, passage:DataType.Passage):
#         self._passageList.append(passage)

#     def get_passage_by(self, tag:str):
#         """
#         tag명을 가지는 패시지만 반환 (순차))
#         """

#         pass

