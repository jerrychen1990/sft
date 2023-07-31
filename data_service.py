#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: chenhao
@time: 2023/7/10 17:02
"""

import pandas as pd
import logging
from snippets import *
import random
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

data = []
labeled_data_path = "/gpfs02/research/data/SFT/processed/labeled.jsonl"
labeled_data_path = "data/parsed/labeled.jsonl"
if not os.path.exists(labeled_data_path):
    jdump_lines([], labeled_data_path)
labeled_data = jload_lines(labeled_data_path)
logging.info(f"load {len(labeled_data)} samples from {labeled_data_path}")
labeled_set = set([x["input"] for x in labeled_data])



labeled_data = []
labeled_set = set()
idx = 0


def _reload_data():
    global data
    global labeled_data
    global labeled_set

    data_paths = ["/gpfs02/research/data/SFT/processed/belle_10k.jsonl",
                  "/gpfs02/research/data/SFT/processed/chat_4k.jsonl",
                  "/gpfs02/research/data/SFT/processed/gen_wordlimit_3k.jsonl"]

    data_paths = ["data/parsed/to_label_part1.jsonl"]
    data = []
    for data_path in data_paths:
        tmp = jload_lines(data_path)
        logging.info(f"load {len(tmp)} samples from {data_path}")
        data.extend(tmp)
    random.shuffle(data)
    logging.info(f"total {len(data)} samples")
    labeled_set = jload_lines(labeled_data_path)
    logging.info(f"load {len(labeled_data)} samples from {labeled_data_path}")
    labeled_set = set([x["input"] for x in labeled_set])


app = Flask(__name__)

_reload_data()


@app.post("/reload_db")
def reload_db():
    logging.info("reload db")
    _reload_data()
    return jsonify(dict(status="ok"))


@app.post("/get_item")
def get_item():
    global idx
    global data
    logging.info(f"getting item:{idx}...")
    item = data[idx]
    idx += 1
    return jsonify(item)


@app.post("/dump_db")
def dump_db():
    logging.info("dump db")
    logging.info(f"dump {len(labeled_data)} samples to {labeled_data_path}")
    jdump_lines(labeled_data, labeled_data_path)
    return jsonify(dict(status="ok", num=len(labeled_data)))


@app.post("/store_item")
def store_item():
    global labeled_data
    item = json.loads(request.data)
    logging.info(f"storing item:{item}...")
    key = item["input"]
    if key not in labeled_set:
        labeled_data.append(item)
        labeled_set.add(item["input"])

    return jsonify(dict(status="ok", labeled_num=len(labeled_data)))


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port='8071')
