#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:03:14 2020

@author: ryepenchi
"""
import getpass

# Your local Username goes here
# If you're testing on your local machine we use a different config,
# to connect to our database

USERNAME = ""

# Configs for the mysql-connector as expected by "connection" and "cursor"
# of your MySQL Database
# When running on the same machine as your scraper
localcfg = {
    "user": "username",
    "password": "password",
    "host": "localhost",
    "database": "database"
}
# When running on a different machine
remotecfg = {
    "user": "username",
    "password": "password",
    "host": "host-address",
    "database": "database",
    "auth_plugin" : "mysql_native_password"
}

if getpass.getuser() == USERNAME:
    cfg = remotecfg
else:
    cfg = localcfg
