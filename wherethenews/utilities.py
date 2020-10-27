#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:03:14 2020

@author: ryepenchi
"""
import argparse
from datetime import datetime

def log(text):
    with open("scrapelog.txt", mode="a") as f:
        format = "%Y-%m-%dT%H:%M"
        dtnow = datetime.now().strftime(format)
        print(dtnow, " >> ", text, file=f)

# Argument parsing Setup
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-a", "--all", action="store_true")
group.add_argument("-n", "--number", type=int)
group.add_argument("-t", "--this",  type=str, help="site URL")
parser.add_argument("-s", "--site", type=str, help="site URL")
parser.add_argument("-c", "--category", type=str)
args = parser.parse_args()

sites = {
    "derstandard": "https://www.derstandard.at/",
    "theguardian": "https://www.theguardian.com/"}