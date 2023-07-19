#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: chenhao
@time: 2023/7/12 18:33
"""
from tqdm import tqdm
import  pandas as pd
from do_predict import generate
from snippets import *
rs = []

algo = "glm130b-sft-360-0712-ckpt1323"
# ip = "172.17.0.2"
ip = "172.16.4.211"


eval_path = "./eval_data/test_360_122.csv"
eval_data = pd.read_csv(eval_path).to_dict(orient="records")
# print(eval_data[0])

print(f"{len(eval_data)} samples in eval data")

rs = []
for item in tqdm(eval_data[:]):
    print(item["input"])
    resp = generate(ip=ip, question=item["input"])
    print(resp)
    item[algo] = resp
    item["winner"] = ""
    item["comment"] = ""
    rs.append(item)


jdump_lines(rs, "./eval_data/test_360_122_0713_v2.csv")



