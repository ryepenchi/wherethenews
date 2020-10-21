#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:03:14 2020

@author: ryepenchi
"""
import contextlib, argparse
from collections import namedtuple

import mysql.connector
from mysql.connector import Error

def log(text):
    with open("scrapelog.txt", mode="a") as f:
        print(text, file=f)

@contextlib.contextmanager
def connection(dbconfig):
    connection = mysql.connector.connect(**dbconfig)
    try:
        yield connection
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()

@contextlib.contextmanager
def cursor(dbconfig):
    with connection(dbconfig) as conn:
        cursor = conn.cursor(buffered=True)
        try:
            yield cursor
        finally:
            cursor.close()

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