#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: chenhao
@time: 2023/7/13 15:17
"""
import math
import random
import re

from icetk import icetk
from snippets import *
from tqdm import tqdm


def try_load(p):
    try:
        ds = jload_lines(p)
        return ds
    except Exception:
        ds = jload(p)
        return ds


def is_valid(item, show=False, no_gpt=True):
    input = item.get("input")
    target = item.get("target")
    if not input or not target:
        return False

    input_list = icetk.encode(item["input"])
    target_list = icetk.encode(item["target"])
    rs = True
    if not 4 <= len(input_list) <= 512:
        rs = False
    if not 8 <= len(target_list) <= 2048:
        rs = False
    input_unk_num = len([x for x in input_list if x == 20000])
    target_unk_num = len([x for x in target_list if x == 20000])
    if input_unk_num >= 2 or target_unk_num >= 2:
        rs = False
    if no_gpt:
        pt = "gpt"
        if re.search(pt, item["input"], re.I) or re.search(pt, item["target"], re.I):
            rs = False

    if not rs and show:
        print(f"item: {item} is not valid")
    return rs


def parse_alpaca_zh(item):
    rs = dict(input=item["instruction"].strip(), target=item["output"].strip(), source="alpaca_gpt4_data_zh")
    return rs


def parse_tigerbot(item):
    rs = dict(input=(item["instruction"] + "\n" + item["input"]).strip(), target=item["output"].strip(),
              source="tigerbot")
    return rs


def parse_belle(item):
    rs = dict(input=(item["instruction"] + "\n" + item["input"]).strip(), target=item["output"].strip(),
              source="belle")
    return rs


def is_literature_generation(item):
    pt = "故事|诗|小说|文案|菜谱|报告|总结|剧本|社论|文章|道歉信|感激信|消化|发言稿|作文|菜谱|对联|教程|评论|短文"
    return re.search(pt, item["input"]) is not None


def extract_word_num(text, pattern="至少(\d+)字|不少于(\d+)字"):
    for e in re.findall(pattern, text):
        for m in e:
            try:
                # print(m)
                rs = int(m.strip())
                return rs
            except Exception as e:
                pass
    return None




def match_word_limit(item):

    tgt_len = len(item["target"])
    ipt = item["input"]
    min_num = extract_word_num(ipt, "[至最]少(\d+)字|不少于(\d+)字")
    if min_num and tgt_len >= min_num:
        return True
    max_num = extract_word_num(ipt, "[至最]多(\d+)字|不多于(\d+)字")
    if max_num and tgt_len <= max_num:
        return True
    around_num = extract_word_num(ipt, "大约(\d+)字|(\d+)字左右")
    if around_num and tgt_len * 0.85 <= around_num <= tgt_len * 1.15:
        return True
    return False

# def parse_share_gpt(item):
#     rs = []
#     pre = ""
#     rd = 1
#     for idx, ele in enumerate(item["conversations"]):
#         if ele["from"] == "human":
#             pre = pre + f"##第 {rd} 轮##\n\n问:{ele['value']}\n\n答:"
#         else:
#             rs.append(dict(input=pre.strip(), target=ele["value"], source="share-gpt"))
#             pre = pre + ele["value"] + "\n\n"
#             rd += 1
#     return rs

def is_chinese(strs, pct=0.4):
    ch_num = 0

    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            ch_num += 1
    return ch_num / len(strs) >= pct


def parse_guanaco_non_chat(item):
    source = "guanaco_non_chat"
    if not item["output"].strip():
        return None

    if is_chinese(item["output"]):
        source += "_cn"

    rs = dict(input=(item["instruction"] + "\n" + item["input"]).strip(), target=item["output"].strip(),
              source=source)
    return rs


def parse_guanaco_chat(item):
    ipt = (item["instruction"] + item["input"]).strip()
    sentences = re.split(r"User:|Assistant:|System:", ipt)
    sentences = [e.strip() for e in sentences if e.strip()]
    # print(sentences)
    # sentences
    sentences += [item["output"].strip()]
    if not len(sentences) % 2 == 0:
        print(f"error in {len(sentences)} sentences")
        for s in sentences:
            print(s)
        return []

    pre = ""
    rs = []
    for idx in range(0, len(sentences), 2):
        rd = idx // 2 + 1
        pmt = pre + f"##第 {rd} 轮##\n\n问:{sentences[idx]}\n\n答:"
        if idx + 1 >= len(sentences):
            break
        ans = sentences[idx + 1].strip()
        if not ans:
            break
        source = "guanaco_chat"
        if is_chinese(ans):
            source += "_cn"
        rs.append(dict(input=pmt.strip(), target=ans, source=source))
        pre = pmt + ans + "\n\n"
    return rs



def _get_sentences_multiturn_chat(instruction):
    cur_sentence = ""
    rs = []
    tag = None
    sentences = re.split("(Assistant:)|(Human:)",instruction, flags=re.I)

    for s in sentences:
        if not s:
            continue
        if s in ["Assistant:", "Human:"]:
            if not tag or tag != s:
                tag = s
                if cur_sentence:
                    rs.append(cur_sentence.strip())
                    cur_sentence = ""
        else:
            cur_sentence += s

    if cur_sentence:
        rs.append(cur_sentence.strip())
    return rs

def parse_belle_multiturn_chat(item):
    ipt = (item["instruction"]).strip()
    sentences = _get_sentences_multiturn_chat(ipt)
    sentences += [item["output"].strip()]
    if not len(sentences) % 2 == 0:
        print(f"error in {len(sentences)} sentences")
        for idx, s in enumerate(sentences):
            print((idx,s))
        return []

    pre = ""
    rd = 1
    rs = []

    for idx, ele in enumerate(sentences):
        if idx %2 == 0:
            pre = pre + f"##第 {rd} 轮##\n\n问:{ele}\n\n答:"
        else:
            rs.append(dict(input=pre.strip(), target=ele, source="multiturn_chat"))
            rd += 1
            pre = pre + ele+ "\n\n"
    return rs

def parse_belle_chat(item):
    ipt = (item["instruction"] + item["input"]).strip()
    sentences = re.split(r"Human:|Assistant:", ipt)
    sentences = [e.strip() for e in sentences if e.strip()]
    # print(sentences)
    # sentences
    sentences += [item["output"].strip()]
    if not len(sentences) % 2 == 0:
        # print(f"error in {len(sentences)} sentences")
        # for idx, s in enumerate(sentences):
        #     print((idx,s))
        return []

    pre = ""
    rs = []
    for idx in range(0, len(sentences), 2):
        rd = idx // 2 + 1
        pmt = pre + f"##第 {rd} 轮##\n\n问:{sentences[idx]}\n\n答:"
        if idx + 1 >= len(sentences):
            break
        ans = sentences[idx + 1].strip()
        if not ans:
            break
        source = "belle_chat"
        rs.append(dict(input=pmt.strip(), target=ans, source=source))
        pre = pmt + ans + "\n\n"
    return rs


def contain_gpt(t):
    t = t.upper()
    return "GPT" in t or "OPENAI" in t


def parse_tsinghua_human_label(item):

    rs = []
    source = "tsinghua_human_label"

    history = item["history"]+[dict(prompt=item["prompt"], response=item["response"])]
    # print(history)
    # print(len(history))
    if len(history) > 1:
        source += "_multichat"
        pre = ""
        for idx, ele in enumerate(item["history"]):
            pre += f"##第 {idx+1} 轮##\n\n问:{ele['prompt']}\n\n答:"
            ans = ele["response"]
            rs.append(dict(input=pre, target=ans, source= source))
            pre += ans + "\n\n"
    else:
        source += "_qa"
        rs = [dict(input=history[0]["prompt"], target=history[0]["response"], source=source)]
    return rs


def parse_share_gpt(item):
    rs = []
    cov = item["conversations"]
    if len(cov) == 2:
        rs = [dict(input=cov[0]["value"], target=cov[1]["value"], source="share-gpt")]
    else:
        pre = ""
        sentences = [e["value"] for e in cov]
        for idx in range(0, len(sentences), 2):
            rd = idx // 2 + 1
            pmt = pre + f"##第 {rd} 轮##\n\n问:{sentences[idx]}\n\n答:"
            if idx + 1 >= len(sentences):
                break
            ans = sentences[idx + 1].strip()
            if not ans:
                break
            source = "share-gpt_chat"
            rs.append(dict(input=pmt.strip(), target=ans, source=source))
            pre = pmt + ans + "\n\n"
    return rs


def process_moss_qa(item):
    # item
    sentences = re.split(r"<eoh>|<eoa>", item["plain_text"])
    sentences = [e[e.index(":") + 1:].strip() for e in sentences if ":" in e]
    # sentences
    assert len(sentences) % 2 == 1
    pre = ""
    rs = []
    for idx in range(0, len(sentences), 2):
        rd = idx // 2 + 1
        pmt = pre + f"##第 {rd} 轮##\n\n问:{sentences[idx]}\n\n答:"
        ans = sentences[idx + 1]
        rs.append(dict(input=pmt, target=ans, source="moss_qa"))
        pre = pmt + ans + "\n\n"

    return rs


def process_moss_multi_chat(item, do_multi_chat=True):
    # item
    chats = item["chat"]
    # chats
    rs = []
    pre =""

    for idx, (t,ele) in enumerate(chats.items()):
        # ele
        human = ele["Human"].replace("<|Human|>: ","").replace("<eoh>","").strip()
        moss = ele["MOSS"].replace("<|MOSS|>: ","").replace("<eom>","").strip()
        human, moss
        if not do_multi_chat:
            rs.append(dict(input=human, target=moss, source="moss_qa"))
        else:
            q = \
    f'''##第 {idx+1} 轮##
    问:{human}

    答:
    ''' 
            a = moss
            pre = pre + "\n\n" + q
            rs.append(dict(input=pre.strip(), target=a.strip(), source="moss_multi_chat"))
            pre += a
    return rs



def parse_data(data, func):
    rs = []
    for idx, item in enumerate(tqdm(data[:])):
        try:
            tmp = func(item)
            if tmp:
                rs.append(tmp)
            else:
                pass
        except:
            pass
    print(f"origin rs len:{len(rs)}")
    if isinstance(rs[0], list):
        rs = flat(rs)
    print(f"parsed rs len:{len(rs)}")
    print(f"sample rs item :{random.choice(rs)}")
    return rs


def view_data(data, sample_num=10):
    sample = random.sample(data, min(len(data), sample_num))
    for item in sample:
        print(item["input"])
        print("*" * 30)
        print(item["target"])
        print("*" * 30)
        print(item["source"])
        print("*" * 30)
        print("\n\n")


def equal_sample(sources, tgt_num):
    rs = []
    t_num = int(math.ceil(tgt_num / len(sources)))
    for s in sources:
        # print(len(s))
        # print(t_num)
        print(f"sample {t_num} from {len(s)}")
        assert len(s) > t_num
        rs.extend(random.sample(s, t_num))
    return rs[:tgt_num]


if __name__ == "__main__":
    print(match_word_limit(dict(input="写一篇609999字左右的作文")))
