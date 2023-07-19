#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

@author: chenhao
@time: 2023/7/14 17:05
"""
import requests
import streamlit as st
from time import sleep
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

host = "http://172.16.0.105:8071"

host = "http://localhost:8071"


logging.info("rerun")


def get_item():
    logging.info("get new item")
    resp = requests.post(f"{host}/get_item")
    # st.session_state["item"] = resp.json()
    return resp.json()


def post_item(data):
    resp = requests.post(f"{host}/store_item", json=data)
    rs = resp.json()
    return rs


def on_accept():
    logging.info("on accept")
    item.update(input_type=st.session_state.input_type, input=st.session_state.input_text,
                target=st.session_state.target_text,
                label="Accept")
    # st.json(item)
    post_item(item)
    st.session_state.accept += 1


def on_deny():
    logging.info("on deny")
    item.update(input_type=st.session_state.input_type, input=st.session_state.input_text,
                target=st.session_state.target_text,
                label="Deny")
    post_item(item)
    st.session_state.deny += 1


st.set_page_config(layout="wide")

input_types = ["Generation", "OpenQA", "Brainstorming", "Chat", "Rewrite", "Summarization", "Classification", "CloseQA",
               "Extract", "Other"]

if "total" not in st.session_state:
    st.session_state.total = 0
    st.session_state.accept = 0
    st.session_state.deny = 0

with st.form("my_form"):
    item = get_item()
    info = f"{st.session_state.total} labeled, {st.session_state.accept} accept, {st.session_state.deny} deny"
    st.info(info)
    ipt = st.text_area(f"Input from {item['source']}", key="input_text", value=item["input"], height=100)
    tgt = st.text_area("Target", key="target_text", value=item["target"], height=300)
    input_type = st.selectbox("Input Type", key="input_type", options=input_types)
    col1, col2 = st.columns(2)
    accept = st.form_submit_button("通过", on_click=on_accept)
    deny = st.form_submit_button("放弃", on_click=on_deny)