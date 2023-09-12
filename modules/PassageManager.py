"""
여러 패시지 정보를 저장하고, 제어/관리를 위한 객체
"""

import modules.DataType as DT

class DataType:
    Passage = DT.Passage
    Sentence = DT.Sentence
    Tag = DT.Tag


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

    stackedPassage:DataType.Passage = DataType.Passage()
    keyword = ""
    
    # Header1, Header2 기준으로 Passage 분리
    for curSentence in sentenceList:
        curSentence:DataType.Sentence = curSentence # type converting

        # check Header
        if DataType.Tag.is_passage_header(curSentence.tag):
            # Key Header (문서의 시작 Header)
            if not stackedPassage.title:
                keyword = stackedPassage.title = curSentence.context
                # stackedPassage.keyword = keyword  # 키워드 패시지에 키워드를 그대로 저장하려는 경우 사용 (self keywording)
                
            # Sub Passage (Key Header 이후의 Header)
            else:
                # 현재까지 정보 저장 후 초기화
                passageList.append(stackedPassage)
                stackedPassage = DataType.Passage(title=curSentence.context, keyword=keyword)
        else:
            stackedPassage.contents += "\n"+curSentence.context
    else:
        # 마지막 Passage 추가
        passageList.append(stackedPassage)

    return passageList

# class PassageManager:
#     def __init__(self) -> None:
#         self._passageList = []

#     def add_passge(self, passage:DataType.Passage):
#         self._passageList.append(passage)

#     # TODO 구현필요
#     def get_passage_by(self, tag:str):
#         """
#         tag명을 가지는 패시지만 반환 (순차))
#         """

#         pass
