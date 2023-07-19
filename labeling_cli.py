#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: chenhao
@time: 2023/7/14 15:57
"""
from snippets import *

input_type_dict = {
    "G": "Generation",
    "C": "Chat",
    "R": "Rewrite",
    "S": "Summarization",
    "O": "OpenQA",
    "Q": "CloseQA",
    "B": "Brainstorming",
    "L": "Classification",
    "T": "Other"
}


def show_item(item):
    print("*" * 20 + item["source"] + "*" * 20)
    print(item["input"])
    print("*" * 40)
    print(item["target"])
    print("*" * 40)


if __name__ == "__main__":
    print("loading data...")
    data = jload_lines("/gpfs02/research/data/SFT/processed/belle_10k.jsonl")

    for idx, item in enumerate(data[:2]):
        print("*" * 20 + f"第{idx + 1}条" + "*" * 20)
        show_item(item)

        while not item.get("input_type"):
            print(
                "选择问题类别:\n([G]eneration)/([C]hat)/(R)ewrite/(S)ummarization/(O)penQA/Close(Q)A/(B)rainstorming/C(L)assification()/O(T)her:")
            ipt = input()
            item["input_type"] = input_type_dict.get(ipt.upper().strip())
        while not item.get("label"):
            print("选择标注:\n(P)ass通过/(A)bort舍弃/Edit(I)nput修改输入/Edit(O)utput修改输出")
            ipt = input().upper().strip()
            if ipt in ["P", "A"]:
                print(f"upload {ipt}")
                item["label"] = ipt
            if ipt in ["I", "E"]:
                print("请输入修改后的内容回车键确认")
                text = input().upper().strip()
                if ipt == "I":
                    item["input"] = ipt
                else:
                    item["target"] = ipt
                show_item(item)
        print("\n\n")
