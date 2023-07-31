#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: chenhao
@time: 2023/7/12 18:33
"""
import concurrent.futures
from tqdm import tqdm
import pandas as pd
from do_predict import generate_new, generate
from snippets import *
import traceback

rs = []

algo = "glm130b-sft-360-0727-ckpt150"

ip = "localhost"
port = "5001"

sst = time.time()

eval_path = "./eval_data/test_360_122.csv"
eval_data = pd.read_csv(eval_path).to_dict(orient="records")
# print(eval_data[0])

print(f"{len(eval_data)} samples in eval data")


def process(idx, item):
    st = time.time()
    try:
        print(f"[{idx}] input:{item['input'][:40]}")
        resp = generate(ip=ip, port=port, question=item["input"])
        # print(resp)
    except Exception as e:
        print(f"error:{e}")
        traceback.print_exc()
        resp = None

    item[algo] = resp
    item["winner"] = ""
    item["comment"] = ""
    rs.append(item)
    print(f"[{idx}] item finished in {time.time() - st: 2.2f}s")
    tgt_path = f"./eval_data/test_{algo}.jsonl"
    jdump_lines(rs, tgt_path)
    cost = time.time() - sst
    v = cost/len(rs)
    print(f"{len(rs)}/{len(eval_data)} [{len(rs)/len(eval_data):2.2%}] done, cost {cost:2.2f}s, {v:2.2f}s per sample, {v*(len(eval_data)-len(rs)):2.2f}s to go")





def process_batch(idx, batch):
    st = time.time()
    print(f"processing batch:{idx}")
    for item in batch[:]:
        process(idx, item)
    print(f"batch{idx} finished in {time.time() - st: 2.2f}s")
    


from icetk import icetk


keys = ["chatglm-130b", algo]



from concurrent.futures import ThreadPoolExecutor, as_completed


eval_data = eval_data[:]


rs = []
num_threads = 4
batch_size = 10

tasks = []
with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:

    for idx, batch in enumerate(get_batched_data(eval_data, batch_size=batch_size)):
        tasks.append(executor.submit(lambda x: process_batch(*x), (idx, batch)))                    

print(f"{len(tasks)} tasks submitted")

for future in as_completed(tasks):
    data = future.result()
    # print("one task finished")



cost = time.time() - sst
print(f"all finished in {cost:2.2}s,  {cost/len(eval_data):2.2f}s per sample)")

tgt_path = f"./eval_data/test_{algo}.jsonl"
print(f"dump to {tgt_path}")
jdump_lines(rs, tgt_path)



def jsonl2df(data):
    rs = []
    for item in data[:]:
        # item
        for k in keys:
            input_list = icetk.tokenize(item[k])
            word_num = int(len(input_list) * 1.8)
            item.update({
                f"{k}-wordnum":word_num,
                f"{k}-score":"",
                f"{k}-comment":""
            })
        rs.append(item)
    len(rs)
    df = pd.DataFrame.from_records(rs)

    columns = ["input", "input_type"]
    for key in keys:
        columns.extend([key, f"{key}-wordnum", f"{key}-score", f"{key}-comment"])

    df = df[columns]
    return df


df = jsonl2df(rs)
df.to_csv(f"./eval_data/test_{algo}.csv", index=False)

