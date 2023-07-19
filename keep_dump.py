#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: chenhao
@time: 2023/7/14 19:30
"""

import requests
import time

host = "http://172.16.0.105:8071"
host = "http://localhost:8071"


import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

while True:
    logging.info("dump db")
    resp = requests.post(f"{host}/dump_db")
    if resp.status_code == 200:
        logging.info(resp.json())
    time.sleep(60)
