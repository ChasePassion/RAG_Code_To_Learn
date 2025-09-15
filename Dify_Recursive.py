# Dify RecursiveCharacterTextSplitter学习文件

## 学习顺序建议（请依据个人能力自定义）

### 第一阶段：理解整体流程
1. 首先看一遍代码，试着自己或者用AI回答一些问题，不建议直接把问题喂给AI
2. 在看的过程中，你同时会冒出很多问题，一个一个解决即可
3. 弄懂大致的流程之后，手绘出一个粗糙的程序执行流程图

### 第二阶段：深入理解代码实现
1. 下一步建议把代码抄一遍，按照程序执行流程图的顺序抄
2. 抄的时候思考，数据的输入和输出具体是怎么样的，数据如何在流程中流动的，有时候你可能发现你只抄没思考，这时候建议删掉重来
3. 各种if具体是什么含义，敲完一遍之后可能还有很多问题，再去解决
4. 抄完一遍之后，可以用一些文本来测试，print看看数据的具体结构

### 第三阶段：精细化理解
1. 然后在第一个程序执行流程图的基础上画出一个更加精细的程序执行流程图
2. 学习大概到这里就结束了，下一个阶段就是手撕算法，视个人喜好及需要进阶

---
import re
import copy
from abc import ABC, abstractmethod
from collections.abc import Callable, Collection, Iterable, Sequence, Set
from typing import (
    Any,
    Optional,
)


def _split_text_with_regex(text:str,separator:str,keep_separator:bool)->list[str]:
    # 问题：这个函数的作用是什么？
    # 问题：keep_separator参数的作用是什么？当它为True和False时，分割结果有什么不同？
    if separator:
        if keep_separator:
            _splits=re.split(f"({re.escape(separator)})",text)
            splits=[_splits[i-1]+_splits[i] for i in range(1,len(_splits),2)]
            # 问题：这个列表推导式的作用是什么？为什么步长是2？
            # 问题：这里的splits是一个列表，除了最后一个元素之外，每个元素的结尾都是有separator的，这种设计有什么好处？
            if len(_splits)%2!=0:
                splits+=_splits[-1:]
                # 问题：什么情况下_splits的长度会是奇数？这时为什么要加上最后一个元素？
        else:
            splits=re.split(separator,text)
            # 问题：当keep_separator为False时，为什么不需要使用re.escape？
    else:
        splits=list(text)
        # 问题：当separator为空字符串时，为什么要把文本转换为单个字符的列表？
    
    return [s for s in splits if (s not in {"","\n"})]
    
class TextSplitter():
    def __init__(
        self,
        chunk_size:int=4000,
        chunk_overlap:int=200,
        length_function:Callable[[list[str]],list[int]]=lambda x:[len(x) for x in x],#实际上就是一个默认函数，接收一个文本片段，然后返回这个文本片段的字数，按照character计算
        keep_separator:bool=False,
    )->None:
    
        if chunk_overlap>chunk_size:
            raise ValueError(
                f"Got a larger chunk overlap ({chunk_overlap}) than chunk size ({chunk_size}), should be smaller."
            )
        self._chunk_size=chunk_size
        self._chunk_overlap=chunk_overlap
        self._length_function=length_function
        self._keep_separator=keep_separator

    @abstractmethod
    def split_text(self,text:str)->list[str]:
        """别删这行"""
        # 问题：这个方法的设计意图是什么？它应该返回什么样的结果？

    def _join_docs(self,docs:list[str],separator:str)->Optional[str]:
        # 问题：这个方法的作用是什么？在什么情况下会被调用？
        text=separator.join(docs)
        text=text.strip()
        if text=="":
            return None
        else:
            return text


    def _merge_splits(self,splits:Iterable[str],separator:str,lengths:list[int])->list[str]:
        # 问题：这个方法的作用是什么？什么情况下会出现重叠？这个方法和后面调用的递归有什么联系？
        # 问题：splits这个参数代表什么？
        separator_len=self._length_function([separator])[0]
        docs=[]
        current_doc:list[str]=[]
        total=0
        # 问题：docs、current_doc、total这三个变量的作用分别是什么？
        for d,_len in zip(splits,lengths):
            # 问题：splits是一个以按照分隔符分割开来的片段为元素的列表，这种说法准确吗？
            if total+_len+(separator_len if len(current_doc)>0 else 0)>self._chunk_size:
                # 问题：这个条件判断的逻辑是什么？为什么要考虑current_doc的长度？
                # 问题：separator_len if len(current_doc)>0 else 0这个表达式的含义是什么？
                if total>self._chunk_size:
                    print(
                        f"Created a chunk of size {total}, which is longer than the specified {self._chunk_size}"
                    )
                    # 问题：什么情况下会出现total大于chunk_size的情况？这正常吗？
                if len(current_doc)>0:
                    doc=self._join_docs(current_doc,separator)
                    if doc is not None:
                        docs.append(doc)
                        # 问题：为什么在添加doc之前需要检查doc is not None？

                    while total>self._chunk_overlap or(
                        total+_len+(separator_len if len(current_doc)>0 else 0)>self._chunk_size and total>0
                    ):
                        # 问题：这个while循环的作用是什么？为什么要同时检查两个条件？
                        # 问题：chunk_overlap在这个循环中起到了什么作用？
                        total-=self._length_function([current_doc[0]])[0]+(#将doc添加到docs之后，需要去除current_doc里面的片段，我们从头开始去除，只保留重叠部分，这里的代码仅更新大小，具体的去除代码在后面
                            separator_len if len(current_doc)>1 else 0
                        )
                        current_doc=current_doc[1:]
                        # 问题：为什么删除第一个元素就能实现重叠效果？这种删除方式有什么特点？
            current_doc.append(d)
            total+=_len+(separator_len if len(current_doc)>1 else 0)
            # 问题：为什么在添加新片段后，total的计算方式与之前的条件判断不同？
        doc =self._join_docs(current_doc,separator)
        if doc is not None:
            docs.append(doc)
            # 问题：为什么在循环结束后还需要再次执行_join_docs和append操作？
        return docs

class RecursiveCharacterTextSplitter(TextSplitter):
    def __init__(
        self,
        separators:Optional[list[str]]=None,
        keep_separator:bool=True,
        **kwargs:Any,
    )->None:
        """**kwargs: Any 是 Python 中一个特殊的参数，它允许函数接受任意数量的关键字参数。
        在 RecursiveCharacterTextSplitter 类的 __init__ 方法中，**kwargs 的作用是将所有未明确列出的关键字参数收集到一个字典中，然后将这些参数传递给父类 TextSplitter 的 __init__ 方法。
        这使得 RecursiveCharacterTextSplitter 可以灵活地接受并传递 TextSplitter 可能需要的任何其他初始化参数，而无需在 RecursiveCharacterTextSplitter 的定义中显式地列出它们。"""
        # 问题：为什么RecursiveCharacterTextSplitter需要单独定义separators参数？
        super().__init__(keep_separator=keep_separator,**kwargs)
        self._separators=separators or ["\n\n","\n"," ",""]
    # 问题：什么是递归分割？这种分割方式相比普通分割有什么优势？
    # 问题：为什么separators的顺序很重要？这影响了分割的什么特性？

    def _split_text(self,text:str,separators:list[str])->list[str]:
        # 问题：这个私有方法的作用是什么？
        final_chunks=[]
        separator=separators[-1]
        new_separators=[]
        # 问题：为什么separator初始化为separators的最后一个元素？这样设计有什么考虑？

        for i,_s in enumerate(separators):
            # 问题：这个for循环的目的是什么？为什么需要遍历所有的分隔符？
            if _s=="":
                separator=_s
                break
                # 问题：为什么当_s为空字符串时要立即break？空字符串作为分隔符有什么特殊含义？
            if re.search(_s,text):#设置遍历是优先使用粗的且存在于文本中的分隔符
                separator=_s
                new_separators=separators[i+1:]
                break
                # 问题：为什么找到了匹配的分隔符后要break？这样保证了什么特性？
                # 问题：new_separators的作用是什么？为什么是separators[i+1:]？
        splits=_split_text_with_regex(text,separator,self._keep_separator)
        #所以这里的splits实际上是一个保留分割符的按\n\n去分割得到的列表
        # 问题：为什么这里要调用_split_text_with_regex函数？这个调用在整个流程中起到了什么作用？
        _good_splits=[]
        _good_splits_lengths=[]
        _separator="" if self._keep_separator else separator
        s_lens=self._length_function(splits)
        # 问题：_good_splits和_good_splits_lengths的作用分别是什么？
        # 问题：_separator的赋值逻辑是什么？为什么keep_separator会影响它的值？
        for s,s_len in zip(splits,s_lens):
            # 问题：这个内层for循环的作用是什么？它与外层循环有什么关系？
            if s_len<self._chunk_size:
                _good_splits.append(s)
                _good_splits_lengths.append(s_len)
            else:
                if _good_splits:
                    merged_text=self._merge_splits(_good_splits,_separator,_good_splits_lengths)
                    final_chunks.extend(merged_text)
                    _good_splits=[]
                    _good_splits_lengths=[]
                    # 问题：为什么要清空_good_splits和_good_splits_lengths？
                if not new_separators:
                    final_chunks.append(s)
                    # 问题：什么情况下new_separators会为空？
                else:
                    other_info=self._split_text(s,new_separators)
                    # 问题：这里为什么会出现递归调用？递归的参数是什么？
                    final_chunks.extend(other_info)

                    """当other_info可以显示章节的完整内容的时候，这意味着分割符使用的是换行符，不能的时候使用的是空格
                       而空格是分割不出来东西的，由于文章的特殊结构，因此这就是为什么上面的splits里面会有
                       元素都是一个字符的情况，这时候new_separators为空"""
                    # 问题：这段注释描述了什么特殊情况？这种情况在什么文本中会出现？
        if _good_splits:
            merged_text=self._merge_splits(_good_splits,_separator,_good_splits_lengths)
            final_chunks.extend(merged_text)
            # 问题：为什么在循环结束后还要再次检查和处理_good_splits？
        return final_chunks
    def split_text(self,text:str)->list[str]:
        return self._split_text(text,self._separators)